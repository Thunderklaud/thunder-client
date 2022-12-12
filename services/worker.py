import shutil
import os
import io
from glob import iglob
from services.localappmanager import LocalAppManager
import requests
from config import Config
from utils.file import uniqueFolderPath, uniqueFilePath, remoteFileOrFolderExists, removeBaseURL
from utils.request import getRequestURL, getRequestHeaders


class Worker:

    def start(self):
        self.syncFolderPath = LocalAppManager.getSetting(
            "local_sync_folder_path")

        # create sync folder if not exists
        if not os.path.isdir(self.syncFolderPath):
            os.makedirs(self.syncFolderPath)

        # create local folders
        self.remoteFilesAndFolders = Worker.__downloadRemoteContentRecursive(
            self)

        # delete local folders that does not exists on the server
        Worker.__deleteFilesAndFoldersNotOnServer(self)

    @staticmethod
    def __downloadRemoteContentRecursive(self, parent_id=None, path=""):
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
                fileResult = Worker.__downloadFile(self, file, path)
                result.append(fileResult)

        # loop dirs
        for dir in dirs:
            folder = {}
            folderID = dir["id"]["$oid"]
            folderName = dir["name"]

            # create local folder
            folderPath = self.syncFolderPath + "/" + path + "/" + folderName
            folderPath = uniqueFolderPath(folderPath)
            if not os.path.isdir(folderPath):
                os.makedirs(folderPath)

            childPath = uniqueFolderPath(path + "/" + folderName)
            folder["id"] = folderID
            folder["name"] = folderName
            folder["path"] = childPath
            result += Worker.__downloadRemoteContentRecursive(self,
                                                              folderID, childPath)

            result.append(folder)

        return result

    @staticmethod
    def __downloadFile(self, file, path):
        fileResult = {}

        fileID = file["uuid"]
        fileName = file["name"]
        filePath = uniqueFilePath(self.syncFolderPath +
                                  "/" + path + "/" + fileName)

        fileResult["id"] = fileID
        fileResult["name"] = fileName
        fileResult["path"] = uniqueFilePath(path + "/" + fileName)

        # do server request
        request_url = getRequestURL("/data/download/file")
        headers = getRequestHeaders()

        # build request data
        request_url += "?uuid=" + fileID

        response = requests.get(url=request_url, json={}, headers=headers)

        # create and write local file
        fileHandle = io.open(filePath, "wb")
        fileHandle.write(response.text.encode("utf-8"))
        fileHandle.close()

        return fileResult

    @staticmethod
    def __deleteFilesAndFoldersNotOnServer(self):
        for path in iglob(self.syncFolderPath + '/**/**', recursive=True):
            absolutePath = path

            # unique paths
            if os.path.isdir(path):
                path = uniqueFolderPath(path)
            else:
                path = uniqueFilePath(path)

            path = removeBaseURL(path, os.path.isfile(path))

            # don't delete root path
            if path != "/" and path != "":

                if not remoteFileOrFolderExists(self.remoteFilesAndFolders, path):

                    # delete folder
                    if os.path.isdir(absolutePath):
                        fullPath = uniqueFolderPath(
                            self.syncFolderPath + path)
                        if os.path.isdir(fullPath):
                            shutil.rmtree(fullPath)

                    else:   # delete file
                        fullPath = uniqueFilePath(self.syncFolderPath + path)
                        if os.path.exists(fullPath):
                            os.remove(fullPath)
                        print("delete file " + path)
