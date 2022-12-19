import requests
from watchdog.events import FileSystemEventHandler
from services.serversettings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.file import removeBaseURL, getDirectoryOrFileName, getDirectoryPath


class FileSyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        if event.event_type == "moved":
            src_path = event.src_path.replace("\\", "/")
            dest_path = event.dest_path.replace("\\", "/")
            FileSyncHandler.__renameFile(src_path, dest_path)

        if event.event_type == "created":
            src_path = event.src_path.replace("\\", "/")
            FileSyncHandler.createFile(src_path)

        if event.event_type == "modified":
            FileSyncHandler.__modifyFile(event)

    @staticmethod
    def createFile(src):
        print("create file: " + src)

        # get current directory
        directoryPath = getDirectoryPath(src)
        remoteDirectory = FileSyncHandler.__getRemoteDirectory(directoryPath)
        print(remoteDirectory)

        if remoteDirectory:
            # get created file
            files = {"file": open(src, "rb")}

            request_url = getRequestURL("/data/file")
            request_url += "?directory=" + remoteDirectory["id"]

            headers = getRequestHeaders(True, "")
            requests.put(
                url=request_url, files=files, headers=headers)
        else:
            print("ERR: remote directory not found")

    @staticmethod
    def __renameFile(src, dest):
        print("renamed file " + src + " to " + dest)

        remoteFile = FileSyncHandler.__getRemoteFile(src)

        if remoteFile:
            newName = getDirectoryOrFileName(dest)
            request_url = getRequestURL("/data/file")

            data = {"uuid": remoteFile["id"], "new_name": newName}

            headers = getRequestHeaders()
            requests.patch(
                url=request_url, json=data, headers=headers)

    @staticmethod
    def deleteFile(event):
        src_path = event.src_path.replace("\\", "/")
        print("delete file: " + src_path)

        remoteFile = FileSyncHandler.__getRemoteFile(src_path)

        if remoteFile:
            request_url = getRequestURL("/data/file")
            request_url += "?uuid=" + remoteFile["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)

            if response.status_code == 404:
                print("INFO: file not on remote file system")
        else:
            print("ERR: File deletion of " + src_path +
                  " not possible, not found on the server")

    @staticmethod
    def __getRemoteFile(path):
        path = removeBaseURL(path, True)

        remoteFiles = ServerSettings.getSyncFiles()

        for remotePath in remoteFiles:
            if "path" in remotePath and remotePath["path"] == path:
                return remotePath

        return {}

    @staticmethod
    def __modifyFile(event):
        src_path = event.src_path.replace("\\", "/")
        print("modify file (delete and create): " + src_path)

        # delete old file
        FileSyncHandler.deleteFile(event)

        # create new file
        FileSyncHandler.createFile(src_path)

    @staticmethod
    def __getRemoteDirectory(path):
        path = removeBaseURL(path, False)

        # search for sync directory by path
        syncDirectories = ServerSettings.getSyncDirectories(False)

        for syncDirectory in syncDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == path:
                return syncDirectory

        return {}
