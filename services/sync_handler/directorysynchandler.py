import requests
from watchdog.events import FileSystemEventHandler
from services.serversettings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.file import removeBaseURL, getDirectoryName, getDirectoryPath


class DirectorySyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        if event.event_type == "moved":
            src_path = event.src_path.replace("\\", "/")
            dest_path = event.dest_path.replace("\\", "/")
            DirectorySyncHandler.__moveDirectory(src_path, dest_path)

        if event.event_type == "created":
            src_path = event.src_path.replace("\\", "/")
            DirectorySyncHandler.__createDirectory(src_path)

    @staticmethod
    def __createDirectory(src):
        print("create directory " + src)

        directoryName = getDirectoryName(src)
        directoryPath = getDirectoryPath(src)

        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(
            directoryPath)
        print(remoteDirectory)

        parentId = ""
        if remoteDirectory:
            parentId = remoteDirectory["id"]

        print("create directory: " + directoryName + " inside " + directoryPath)
        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()
        data = {"parent_id": parentId, "name": directoryName}
        response = requests.post(
            url=request_url, json=data, headers=headers)

    @staticmethod
    def __moveDirectory(src, dest):
        print("move file from " + src + " to " + dest)
        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(src)

        # if remote directory was found
        if remoteDirectory:
            directoryPath = getDirectoryPath(src)
            directoryPath = getDirectoryPath(dest)
            print(directoryPath + ":"+directoryPath)

            directoryName = getDirectoryName(src)
            directoryName = getDirectoryName(dest)
            print(directoryName + ":"+directoryName)

            # moved directory into another
            if (directoryPath != directoryPath and directoryName == directoryName):
                print("TODO: moved directory")
            else:  # renamed directory
                print("renamed directory")
                request_url = getRequestURL("/data/directory")
                headers = getRequestHeaders()
                data = {"id": remoteDirectory["id"], "name": directoryName}
                response = requests.patch(
                    url=request_url, json=data, headers=headers)

    @staticmethod
    def __getRemoteDirectory(path):
        path = removeBaseURL(path, False)

        # search for sync directory by path
        syncDirectories = ServerSettings.getSyncDirectories(False)

        for syncDirectory in syncDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == path:
                return syncDirectory

        return {}

    @staticmethod
    def deleteDirectory(event):
        print("delete directory: " + event.src_path)

        src_path = event.src_path.replace("\\", "/")

        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(src_path)

        if remoteDirectory:
            request_url = getRequestURL("/data/directory")
            request_url += "?id=" + remoteDirectory["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)
        else:
            print("ERR: deletion of " + event.src_path +
                  " not possible. Directory not found on server")
