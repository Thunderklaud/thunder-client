import shutil
import os
from glob import iglob
from services.localappmanager import LocalAppManager
import requests
from config import Config
from utils.folder import uniqieFolderPath, remoteFolderExists, removeBaseURL
from utils.request import getRequestURL, getRequestHeaders


class Worker:

    def start(self):
        self.sync_folder_paths = LocalAppManager.getSetting(
            "local_sync_folder_path")

        # create sync folder if not exists
        if not os.path.isdir(self.sync_folder_paths):
            os.makedirs(self.sync_folder_paths)

        # create local folders
        self.remoteFolders = Worker.__createFolderRecursive(self)

        # delete local folders that does not exists on the server
        Worker.__deleteFoldersNotOnServer(self)

    @staticmethod
    def __createFolderRecursive(self, parent_id=None, path=""):
        result = []

        # build request data
        if parent_id is not None:
            data = {"id": str(parent_id)}
        else:
            data = {}

        # do server request
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()
        response = requests.get(url=request_url, json=data, headers=headers)

        # handle response
        if response.status_code != 200:
            return []
        jsonResponse = response.json()
        dirs = jsonResponse["dirs"]

        # loop the result
        for dir in dirs:
            folder = {}
            folderID = dir["id"]["$oid"]
            folderName = dir["name"]

            # create local folder
            folderPath = self.sync_folder_paths + "/" + path + "/" + folderName
            folderPath = uniqieFolderPath(folderPath)
            if not os.path.isdir(folderPath):
                os.makedirs(folderPath)

            childPath = uniqieFolderPath(path + "/" + folderName)
            folder["id"] = folderID
            folder["name"] = folderName
            folder["path"] = childPath
            result += Worker.__createFolderRecursive(self,
                                                     folderID, childPath)

            result.append(folder)

        return result

    @staticmethod
    def __deleteFoldersNotOnServer(self):
        for path in iglob(self.sync_folder_paths + '/**/**', recursive=True):
            # unique paths
            path = uniqieFolderPath(path)

            # delete folder id it does not exists on server
            if os.path.isdir(path):

                path = removeBaseURL(path)

                # don't delete root path
                if path != "/" and path != "":

                    if not remoteFolderExists(self.remoteFolders, path):

                        # delete folder
                        fullPath = uniqieFolderPath(
                            self.sync_folder_paths + path)
                        if os.path.isdir(fullPath):
                            shutil.rmtree(fullPath)
