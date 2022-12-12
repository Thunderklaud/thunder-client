import shutil
import os
import io
from glob import iglob
from services.localappmanager import LocalAppManager
import requests
from config import Config
from utils.file import uniqueDirectoryPath, uniqueFilePath, remoteFileOrDirectoryExists, removeBaseURL
from utils.request import getRequestURL, getRequestHeaders


class Worker:

    def start(self):
        self.syncDirectoryPath = LocalAppManager.getSetting(
            "local_sync_folder_path")

        # create sync directory if not exists
        if not os.path.isdir(self.syncDirectoryPath):
            os.makedirs(self.syncDirectoryPath)

        # create local directories
        self.remoteFilesAndDirectories = Worker.__downloadRemoteContentRecursive(
            self)

        # delete local directories that does not exists on the server
        Worker.__deleteFilesAndDirectoriessNotOnServer(self)

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
            directory = {}
            directoryID = dir["id"]["$oid"]
            directoryName = dir["name"]

            # create local directory
            directoryPath = self.syncDirectoryPath + "/" + path + "/" + directoryName
            directoryPath = uniqueDirectoryPath(directoryPath)
            if not os.path.isdir(directoryPath):
                os.makedirs(directoryPath)

            childPath = uniqueDirectoryPath(path + "/" + directoryName)
            directory["id"] = directoryID
            directory["name"] = directoryName
            directory["path"] = childPath
            result += Worker.__downloadRemoteContentRecursive(self,
                                                              directoryID, childPath)

            result.append(directory)

        return result

    @staticmethod
    def __downloadFile(self, file, path):
        fileResult = {}

        fileID = file["uuid"]
        fileName = file["name"]
        filePath = uniqueFilePath(self.syncDirectoryPath +
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
    def __deleteFilesAndDirectoriessNotOnServer(self):
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
                        print("delete file " + path)
