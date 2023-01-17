import shutil
import os
import time
import io
import threading
from glob import iglob
from services.localappmanager import LocalAppManager
import requests
from config import Config
from utils.file import uniqueDirectoryPath, uniqueFilePath, remoteFileOrDirectoryExists, removeBaseURL
from utils.request import getRequestURL, getRequestHeaders
from services.sync_handlers.filesynchandler import FileSyncHandler


class PermanentSyncHandler:

    # global variable to set the observers state (0 = offline, 1 = running, 2 = syncing)
    STATUS = 1

    def __init__(self):
        self.syncDirectoryPath = LocalAppManager.getSetting(
            "syncFolderPath")
        self.lastCheck = self.getTimestamp()
        self.run()

    def run(self):
        t1 = threading.Thread(target=self.start)
        t1.start()

    def start(self):
        print("[INFO] Starting permanent syncronisation...")

        # self.runStartup()

        try:
            while PermanentSyncHandler.STATUS != 0:
                time.sleep(10)

                if PermanentSyncHandler.STATUS == 1:
                    self.runStartup()   # Fallback for sync
        except:
            print("PermanentSyncHandler error")

    # TODO: IN PRODUCTION
    def doRemoteCheck(self):
        # do server request
        request_url = getRequestURL("/user/syncstate")
        request_url += "?since=" + str(self.lastCheck)
        headers = getRequestHeaders()

        # build request data
        response = requests.get(url=request_url, json={}, headers=headers)
        changes = response.json()

        for change in changes:
            # CREATE
            if change["type"] == "File" and change["action"] == "create":
                print("PermanentSyncHandler: Create File")
            if change["type"] == "Directory" and change["action"] == "create":
                print("PermanentSyncHandler: Create Directory")

            # RENAME
            if change["type"] == "File" and change["action"] == "rename":
                print("PermanentSyncHandler: Rename File")
            if change["type"] == "Directory" and change["action"] == "rename":
                print("PermanentSyncHandler: Rename Directory")

            # DELETE
            if change["type"] == "File" and change["action"] == "delete":
                print("PermanentSyncHandler: Delete File")
            if change["type"] == "Directory" and change["action"] == "delete":
                print("PermanentSyncHandler: Delete Directory")

        self.lastCheck = self.getTimestamp()

    def getTimestamp(self):
        return int(time.time()*1000.0)

    def runStartup(self):
        PermanentSyncHandler.STATUS = 2
        print("[INFO] Sync local folder '" +
              self.syncDirectoryPath + "' with remote server...")

        # create sync directory if not exists
        if not os.path.isdir(self.syncDirectoryPath):
            os.makedirs(self.syncDirectoryPath)

        # get all dirs that should not be synced
        directoriesNotToSync = LocalAppManager.getSetting("notToSyncFolders")

        # create local directories
        self.remoteFilesAndDirectories = PermanentSyncHandler.__downloadRemoteContentRecursive(
            self, None, "", directoriesNotToSync)

        # delete local directories that does not exists on the server
        PermanentSyncHandler.__deleteFilesAndDirectoriessNotOnServer(
            self, directoriesNotToSync)

        print("[INFO] Sync local folder done")

        PermanentSyncHandler.STATUS = 1
        # self.run()    # TODO: incomment when using doRemoteCheck()
        # if PermanentSyncHandler.STATUS == 2:
        #     self.run()

    @staticmethod
    def __downloadRemoteContentRecursive(self, parent_id=None, path="", directoriesNotToSync=[]):
        result = []

        # do server request
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()

        # build request data
        if parent_id is not None:
            request_url += "?id=" + str(parent_id)
        response = requests.get(url=request_url, json={}, headers=headers)

        # handle response
        if response.status_code != 200:
            return []
        jsonResponse = response.json()
        dirs = jsonResponse["dirs"]
        files = jsonResponse["files"]

        # download files
        if len(files):
            for file in files:
                fileResult = PermanentSyncHandler.__handleFile(
                    self, file, path)
                result.append(fileResult)

        # loop dirs
        for dir in dirs:
            directory = {}
            directoryID = dir["id"]["$oid"]
            directoryName = dir["name"]

            # create local directory
            directoryPath = self.syncDirectoryPath + "/" + path + "/" + directoryName
            directoryPath = uniqueDirectoryPath(directoryPath)

            # only create folder if folder should be synced
            if not directoryID in directoriesNotToSync:
                if not os.path.isdir(directoryPath):
                    os.makedirs(directoryPath)

            childPath = uniqueDirectoryPath(path + "/" + directoryName)
            directory["id"] = directoryID
            directory["name"] = directoryName
            directory["path"] = childPath

            # only get children if folder should be synced
            if not directoryID in directoriesNotToSync:
                result += PermanentSyncHandler.__downloadRemoteContentRecursive(self,
                                                                                directoryID, childPath, directoriesNotToSync)

            result.append(directory)

        return result

    @staticmethod
    def __handleFile(self, file, path):

        fileResult = {}

        fileID = file["uuid"]
        fileName = file["name"]
        filePath = uniqueFilePath(self.syncDirectoryPath +
                                  "/" + path + "/" + fileName)

        fileResult["id"] = fileID
        fileResult["name"] = fileName
        fileResult["path"] = uniqueFilePath(path + "/" + fileName)

        # if local file does not exists => download
        if not os.path.isfile(filePath):
            PermanentSyncHandler.__downloadFile(fileID, filePath)

        else:   # check dates for newer file

            # compare modified dates
            remoteModifiedDate = float(
                file["creation_date"]["$date"]["$numberLong"]) / 1000  # * 1000 to get timestamp in seconds
            localModifiedDate = float(os.path.getmtime(filePath))

            # if remote modified date is newer => download file, else upload file
            if remoteModifiedDate > localModifiedDate:
                PermanentSyncHandler.__downloadFile(fileID, filePath)
            else:
                FileSyncHandler.createFile(filePath)

        return fileResult

    @staticmethod
    def __downloadFile(fileID, filePath):
        # do server request
        request_url = getRequestURL("/data/download/file")
        headers = getRequestHeaders()

        # build request data
        request_url += "?uuid=" + fileID

        response = requests.get(url=request_url, json={},
                                headers=headers, stream=True)

        # create and write local file
        filePath = uniqueFilePath(filePath)
        try:
            fileHandle = io.open(filePath, "wb")
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, fileHandle)
            # fileHandle.write(response.text.encode("utf-8"))
            fileHandle.close()
        except PermissionError:
            print("[ERR] Permission denied")

    @staticmethod
    # TODO: directoriesNotToSync
    def __deleteFilesAndDirectoriessNotOnServer(self, directoriesNotToSync):
        for path in iglob(self.syncDirectoryPath + '/**/**', recursive=True):
            absolutePath = path

            # unique paths
            if os.path.isdir(path):
                path = uniqueDirectoryPath(path)
            else:
                path = uniqueFilePath(path)

            path = removeBaseURL(path, os.path.isfile(path))

            # don't delete root path
            if path != "/" and path != "":

                if not remoteFileOrDirectoryExists(self.remoteFilesAndDirectories, path):

                    # delete directory
                    if os.path.isdir(absolutePath):
                        fullPath = uniqueDirectoryPath(
                            self.syncDirectoryPath + path)
                        if os.path.isdir(fullPath):
                            shutil.rmtree(fullPath)

                    else:   # delete file
                        fullPath = uniqueFilePath(
                            self.syncDirectoryPath + path)
                        if os.path.exists(fullPath):
                            os.remove(fullPath)
