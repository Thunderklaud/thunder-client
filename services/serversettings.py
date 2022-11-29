import requests
from utils.folder import uniqieFolderPath
from utils.request import getRequestURL, getRequestHeaders


class ServerSettings():

    @staticmethod
    def getSyncFolders(multidimensionalArray=True):
        folders = ServerSettings.__getFolderRecursive(
            None, "", multidimensionalArray)
        return folders

    @staticmethod
    def __getFolderRecursive(parentId=None, path="", multidimensionalArray=True):
        result = []

        # build request data
        if parentId is not None:
            data = {"id": str(parentId)}
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

            childPath = uniqieFolderPath(path + "/" + folderName)

            folder["id"] = folderID
            folder["name"] = folderName
            folder["path"] = childPath

            folderChildren = ServerSettings.__getFolderRecursive(
                folderID, childPath, multidimensionalArray)

            # set children as variable
            if multidimensionalArray:
                folder["children"] = folderChildren
            else:
                # add children to arrays root level
                result += folderChildren

            result.append(folder)

        return result
