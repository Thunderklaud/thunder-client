import os
from services.localappmanager import LocalAppManager
import requests
from config import Config


class Worker:

    def start(self):
        print("starting background service worker...")

        self.syncFolderPath = LocalAppManager.getSetting(
            "local_sync_folder_path")

        # create sync folder if not exists
        if not os.path.isdir(self.syncFolderPath):
            os.makedirs(self.syncFolderPath)

        # create local folders
        Worker.__createFolderRecursive(self)

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
            folder["children"] = Worker.__createFolderRecursive(self,
                                                                folderID, childPath)

            result.append(folder)

        return result

    @staticmethod
    def __deleteFoldersNotOnServer(self):
