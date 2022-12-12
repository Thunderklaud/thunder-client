import requests
from watchdog.events import FileSystemEventHandler
from services.serversettings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.file import removeBaseURL, getFolderName, getFolderPath


class FolderSyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        if event.event_type == "moved":
            src_path = event.src_path.replace("\\", "/")
            dest_path = event.dest_path.replace("\\", "/")
            FolderSyncHandler.__moveFolder(src_path, dest_path)

        if event.event_type == "created":
            src_path = event.src_path.replace("\\", "/")
            FolderSyncHandler.__createFolder(src_path)

    @staticmethod
    def __createFolder(src):
        print("create folder " + src)

        folderName = getFolderName(src)
        folderPath = getFolderPath(src)

        remoteFolder = FolderSyncHandler.__getRemoteFolder(folderPath)
        print(remoteFolder)

        parentId = ""
        if remoteFolder:
            parentId = remoteFolder["id"]

        print("create folder: " + folderName + " inside " + folderPath)
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()
        data = {"parent_id": parentId, "name": folderName}
        response = requests.post(
            url=request_url, json=data, headers=headers)

    @staticmethod
    def __moveFolder(src, dest):
        print("move file from " + src + " to " + dest)
        remoteFolder = FolderSyncHandler.__getRemoteFolder(src)

        # if remote folder was found
        if remoteFolder:
            oldFolderPath = getFolderPath(src)
            newFolderPath = getFolderPath(dest)
            print(oldFolderPath + ":"+newFolderPath)

            oldFolderName = getFolderName(src)
            newFolderName = getFolderName(dest)
            print(oldFolderName + ":"+newFolderName)

            # moved folder into another
            if (oldFolderPath != newFolderPath and oldFolderName == newFolderName):
                print("TODO: moved folder")
            else:  # renamed folder
                print("renamed folder")
                request_url = getRequestURL("/data/directory")
                headers = getRequestHeaders()
                data = {"id": remoteFolder["id"], "name": newFolderName}
                response = requests.patch(
                    url=request_url, json=data, headers=headers)

    @staticmethod
    def __getRemoteFolder(path):
        path = removeBaseURL(path, False)

        # search for sync folder by path
        syncFolders = ServerSettings.getSyncFolders(False)

        for syncFolder in syncFolders:
            if "path" in syncFolder and syncFolder["path"] == path:
                return syncFolder

        return {}

    @staticmethod
    def deleteFolder(event):
        print("delete folder: " + event.src_path)

        src_path = event.src_path.replace("\\", "/")

        remoteFolder = FolderSyncHandler.__getRemoteFolder(src_path)

        if remoteFolder:
            request_url = getRequestURL("/data/directory")
            request_url += "?id=" + remoteFolder["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)
        else:
            print("ERR: deletion of " + event.src_path +
                  " not possible. Directory not found on server")
