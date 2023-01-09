import requests
import re
import base64
from utils.file import uniqueDirectoryPath, uniqueFilePath
from utils.request import getRequestURL, getRequestHeaders
from services.localappmanager import LocalAppManager


class ServerSettings():

    @staticmethod
    def getSyncDirectories(multidimensionalArray=True, includeRoot=False):
        directories = ServerSettings.__getDirectoryRecursive(
            None, "", multidimensionalArray)

        # add root directory
        if not multidimensionalArray and includeRoot:
            rootID = ServerSettings.getRootId()
            directories.append(
                {"id": rootID, "name": "", "path": "/", "childCount": 0})

        return directories

    @staticmethod
    def getSyncFiles():
        files = ServerSettings.__getFilesRecursive(None, "")
        return files

    @staticmethod
    def __getDirectoryRecursive(parentId=None, recPath="", multidimensionalArray=True):
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
        files = jsonResponse["files"]

        # loop the result
        for dir in dirs:
            directory = {}
            directoryID = dir["id"]["$oid"]
            directoryName = dir["name"]

            childPath = uniqueDirectoryPath(
                recPath + "/" + directoryName)

            directory["id"] = directoryID
            directory["name"] = directoryName
            directory["path"] = childPath
            directory["childCount"] = len(files)

            directoryChildren = ServerSettings.__getDirectoryRecursive(
                directoryID, childPath, multidimensionalArray)

            # set children as variable
            if multidimensionalArray:
                directory["children"] = directoryChildren
            else:
                # add children to arrays root level
                result += directoryChildren

            result.append(directory)

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
            directory = dir["id"]["$oid"]
            directoryName = dir["name"]

            childPath = uniqueDirectoryPath(path + "/" + directoryName)

            result += ServerSettings.__getFilesRecursive(
                directory, childPath)

        return result

    @staticmethod
    def getRootId():
        token = LocalAppManager.readLocalJWT()

        header, jwt, signature = token.split(".")
        payloadDecoded = str(base64.b64decode(jwt))

        return re.findall(
            r"\$oid\"\:\"([^\"]*)\"", payloadDecoded)[0]
