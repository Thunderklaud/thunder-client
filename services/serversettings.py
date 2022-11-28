import requests
from services.localappmanager import LocalAppManager
from config import Config


class ServerSettings():

    @staticmethod
    def getSyncFolders():
        # add folders to test
        # ServerSettings.__addTestFolders()

        folders = ServerSettings.__getFolderRecursive()
        print(folders)
        print("END")
        return folders

    @staticmethod
    def __getFolderRecursive(parent_id=None):
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

            folder["id"] = folderID
            folder["name"] = folderName
            folder["children"] = ServerSettings.__getFolderRecursive(folderID)

            result.append(folder)

        return result

    @staticmethod
    def __addTestFolders():
        jwt = LocalAppManager.readLocalJWT()
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        requestURL = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"
        res = requests.post(
            url=requestURL, data='{"name": "Doc"}', headers=headers)
        res = requests.post(
            url=requestURL, data='{"name": "Doc 2"}', headers=headers)
        res = requests.post(
            url=requestURL, data='{"name": "Doc 3"}', headers=headers)
