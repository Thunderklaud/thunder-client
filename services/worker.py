import os
from services.localappmanager import LocalAppManager
import requests 
from config import Config


class Worker:

    localSyncFolderPath = "./test/client"

    def start(self):
        # print("start worker")
        syncFolderPath = self.getSyncFolderPath()

        # create sync folder if not exists
        if not os.path.isdir(syncFolderPath):
            os.makedirs(syncFolderPath)

        folders = Worker.__getFolderRecursive();
        print(folders)


    @staticmethod
    def getSyncFolderPath():
        return Worker.localSyncFolderPath

    @staticmethod
    def setLocalSyncFolderPath(path):
        Worker.localSyncFolderPath = path


    @staticmethod
    def __getFolderRecursive(parent_id=None, path=None):
        result = []

        jwt = LocalAppManager.readLocalJWT()
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        requestURL = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"

        # build request data
        if parent_id is not None:
            data = '{"id": "' + str(parent_id) + '"}'
        else:
            data = '{}'

        response = requests.get(url=requestURL, data=data, headers=headers)

        # DEBUG
        print("request" + data)
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
            
            if path is None:
                path = ""

            folderPath = Worker.getSyncFolderPath() + "/" + path + "/" + folderName
            print(folderPath)
            if not os.path.isdir(folderPath):
                os.makedirs(folderPath)

            childPath = path + "/" + folderName 
            folder["id"] = folderID
            folder["name"] = folderName
            folder["children"] = Worker.__getFolderRecursive(folderID, childPath)

            result.append(folder)

        return result
