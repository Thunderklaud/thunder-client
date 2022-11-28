import requests
from services.localappmanager import LocalAppManager
from config import Config


class ServerSettings():

    @staticmethod
    def getSyncFolders(multidimensional_array=True):

        folders = ServerSettings.__getFolderRecursive(
            None, "", multidimensional_array)
        # print(folders)
        # print("END")
        return folders

    @staticmethod
    def __getFolderRecursive(parent_id=None, path="", multidimensional_array=True):
        result = []

        jwt = LocalAppManager.readLocalJWT()
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        request_url = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"

        # build request data
        if parent_id is not None:
            data = {"id": str(parent_id)}
        else:
            data = {}

        response = requests.get(url=request_url, json=data, headers=headers)

        # DEBUG
        print("request: " + str(data))
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
            folder["path"] = path + "/" + folderName

            childPath = path + "/" + folderName

            folderChildren = ServerSettings.__getFolderRecursive(
                folderID, childPath, multidimensional_array)

            # set children as variable
            if multidimensional_array:
                folder["children"] = folderChildren
            else:
                # add children to arrays root level
                result += folderChildren

            result.append(folder)

        return result

    # this method is just to add some test folders (no productive use)
    @staticmethod
    def __addTestFolders():
        jwt = LocalAppManager.readLocalJWT()
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        request_url = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"
        res = requests.post(
            url=request_url, data='{"name": "Doc"}', headers=headers)
        res = requests.post(
            url=request_url, data='{"name": "Doc 2"}', headers=headers)
        res = requests.post(
            url=request_url, data='{"name": "Doc 3"}', headers=headers)
