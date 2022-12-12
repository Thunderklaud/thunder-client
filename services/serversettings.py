import requests
from utils.file import uniqueFolderPath, uniqueFilePath
from utils.request import getRequestURL, getRequestHeaders


class ServerSettings():

    @staticmethod
    def getSyncFolders(multidimensionalArray=True):
        folders = ServerSettings.__getFolderRecursive(
            None, "", multidimensionalArray)
        return folders

    @staticmethod
    def getSyncFiles():
        files = ServerSettings.__getFilesRecursive(None, "")
        return files

    @staticmethod
    def __getFolderRecursive(parentId=None, path="", multidimensionalArray=True):
        result = []

        # do server request
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()

        # build request data
        if parentId is not None:
            request_url += "?id=" + str(parentId)

        response = requests.get(url=request_url, json={}, headers=headers)

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

            childPath = uniqueFolderPath(path + "/" + folderName)

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

    @staticmethod
    def __getFilesRecursive(parentId=None, path=""):
        result = []

        # do server request
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()

        # build request data
        if parentId is not None:
            request_url += "?id=" + str(parentId)

        response = requests.get(url=request_url, json={}, headers=headers)

        # handle response
        if response.status_code != 200:
            return []
        jsonResponse = response.json()
        files = jsonResponse["files"]
        dirs = jsonResponse["dirs"]

        # download files
        if len(files):
            for loopFile in files:
                file = {}

                fileID = loopFile["uuid"]
                fileName = loopFile["name"]

                file["id"] = fileID
                file["name"] = fileName
                file["path"] = uniqueFilePath(path + "/" + fileName)
                result.append(file)

        # loop the result
        for dir in dirs:
            folderID = dir["id"]["$oid"]
            folderName = dir["name"]

            childPath = uniqueFolderPath(path + "/" + folderName)

            result += ServerSettings.__getFilesRecursive(
                folderID, childPath)

        return result
