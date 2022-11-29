import shutil
import os
from glob import iglob
from services.localappmanager import LocalAppManager
import requests
from config import Config


class Worker:

    def start(self):
        self.syncFolderPath = LocalAppManager.getSetting(
            "local_sync_folder_path")

        # create sync folder if not exists
        if not os.path.isdir(self.syncFolderPath):
            os.makedirs(self.syncFolderPath)

        # create local folders
        self.remoteFolders = Worker.__createFolderRecursive(self)

        # delete local folders that does not exists on the server
        Worker.__deleteFoldersNotOnServer(self)

    @staticmethod
    def __createFolderRecursive(self, parent_id=None, path=""):
        result = []

        jwt = LocalAppManager.readLocalJWT()
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        request_url = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"

        # build request data
        if parent_id is not None:
            data = '{"id": "' + str(parent_id) + '"}'
        else:
            data = '{}'

        response = requests.get(url=request_url, data=data, headers=headers)

        # DEBUG
        # print("request" + data)
        # END DEBUG

        if response.status_code != 200:
            return []

        jsonResponse = response.json()
        dirs = jsonResponse["dirs"]

        for dir in dirs:
            folder = {}
            folderID = dir["id"]["$oid"]
            folderName = dir["name"]

            # create local folder
            folderPath = self.syncFolderPath + "/" + path + "/" + folderName
            if not os.path.isdir(folderPath):
                os.makedirs(folderPath)

            childPath = path + "/" + folderName
            folder["id"] = folderID
            folder["name"] = folderName
            folder["path"] = path + "/" + folderName

            result += Worker.__createFolderRecursive(self,
                                                     folderID, childPath)

            result.append(folder)

        return result

    @staticmethod
    def __deleteFoldersNotOnServer(self):
        for path in iglob(self.syncFolderPath + '/**/**', recursive=True):
            # unique paths
            path = path.replace("\\", "/")

            # delete folder id it does not exists on server
            if os.path.isdir(path):

                # remove base URL for comparation
                localPathLength = len(
                    LocalAppManager.getSetting("local_sync_folder_path")) - 1  # -1 to hold the slash at the beginning
                pathLength = len(path)
                path = path[localPathLength:pathLength]

                # don't delete root path
                if path != "/" and path != "":

                    # remove slash at the end
                    path = path.rstrip("/")

                    if not Worker.__remoteFolderExists(self, path):
                        # remove slash at the beginning
                        path = path.lstrip("/")

                        # delete folder
                        fullPath = self.syncFolderPath + path
                        if os.path.isdir(fullPath):
                            shutil.rmtree(fullPath)
                            print("deleted " + fullPath +
                                  " (does not exists on the server)")

    @staticmethod
    def __remoteFolderExists(self, path):
        for folder in self.remoteFolders:
            if "path" in folder and folder["path"] == path:
                return True

        return False
