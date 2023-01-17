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
from services.server_settings import ServerSettings


class PermanentSyncHandler:

    # global variable to set the observers state (0 = offline, 1 = running, 2 = syncing)
    STATUS = 1
    localSyncState = {}

    def __init__(self):
        self.syncDirectoryPath = LocalAppManager.getSetting(
            "syncFolderPath")
        self.lastCheck = LocalAppManager.getSetting("lastSyncState")

        # download all data on first startup
        if self.lastCheck == 0:
            self.runStartup()

        # run permanent syncronizer
        self.run()

    def run(self):
        t1 = threading.Thread(target=self.start)
        t1.start()

    def start(self):
        print("[INFO] Starting permanent synchronisation...")

        # try:
        while PermanentSyncHandler.STATUS != 0:
            time.sleep(10)
            self.doRemoteCheck()
        # except:
            #print("PermanentSyncHandler error")

    def __getLatestSyncStateEntry(self, entries):
        # return current timestamp if no entries
        if len(entries) == 0:
            return self.__getCurrentTimestamp()

        max = 0
        for entry in entries:
            entryChangeDate = int(
                entry["creation_date"]["$date"]["$numberLong"])

            if entryChangeDate > max:
                max = entryChangeDate

        return max + 1  # +1 to exclude to current change

    def doRemoteCheck(self):
        print("do remote check since " + str(self.lastCheck))
        # do server request
        request_url = getRequestURL("/user/syncstate")
        request_url += "?since=" + str(self.lastCheck)
        headers = getRequestHeaders()

        # build request data
        response = requests.get(url=request_url, json={}, headers=headers)
        changes = response.json()

        if len(changes) > 0:
            syncDirectories = ServerSettings.getSyncDirectories(False)
            syncFiles = ServerSettings.getSyncFiles()

            for change in changes:
                id = change["corresponding_id"]["$oid"]

                # CREATE
                if change["type"] == "File" and change["action"] == "create":
                    print("PermanentSyncHandler: Create File")
                if change["type"] == "Directory" and change["action"] == "create":
                    remoteDir = self.__getRemoteDirectory(syncDirectories, id)
                    print(remoteDir)
                    print("PermanentSyncHandler: Create Directory")

                # RENAME
                if change["type"] == "File" and change["action"] == "rename":
                    print("PermanentSyncHandler: Rename File")
                if change["type"] == "Directory" and change["action"] == "rename":
                    remoteDir = self.__getRemoteDirectory(syncDirectories, id)
                    print("PermanentSyncHandler: Rename Directory (TODO)")

                # DELETE
                if change["type"] == "File" and change["action"] == "delete":
                    print("PermanentSyncHandler: Delete File")
                if change["type"] == "Directory" and change["action"] == "delete":
                    from services.sync_handlers.directorysynchandler import DirectorySyncHandler
                    remoteDir = self.__getRemoteDirectory(syncDirectories, id)
                    print(id)
                    print(syncDirectories)
                    DirectorySyncHandler.deleteDirectory(remoteDir["path"])
                    print("PermanentSyncHandler: Delete Directory")
        else:
            print("[INFO] No remote changes since last check")

        self.lastCheck = self.__getCurrentTimestamp()
        PermanentSyncHandler.localSyncState = changes
        LocalAppManager.saveSetting("lastSyncState", str(self.lastCheck))

    @ staticmethod
    def __getRemoteDirectory(syncDirectories, id):

        # search for sync directory by path
        for syncDirectory in syncDirectories:
            if "id" in syncDirectory and syncDirectory["id"] == id:
                return syncDirectory

        return {}

    def removeEntryFromLocalSyncState(id):
        if PermanentSyncHandler.localSyncState is []:
            return

        print("before" + str(len(PermanentSyncHandler.localSyncState)))
        obj = []

        for entry in PermanentSyncHandler.localSyncState:
            if entry["corresponding_id"]["$oid"] == id:
                obj = entry
                print("REMOVE:::")
                print(obj)

        if obj is not [] and obj in PermanentSyncHandler.localSyncState:
            PermanentSyncHandler.localSyncState.remove(obj)
        print("after" + str(len(PermanentSyncHandler.localSyncState)))

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

        self.lastCheck = self.__getCurrentTimestamp()
        PermanentSyncHandler.STATUS = 1

    def __getCurrentTimestamp(self):
        return int(time.time()*1000.0)

    @ staticmethod
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

    @ staticmethod
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

    @ staticmethod
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

    @ staticmethod
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
