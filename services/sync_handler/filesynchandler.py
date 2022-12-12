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
            FileSyncHandler.__moveFile(src_path, dest_path)

        if event.event_type == "created":
            src_path = event.src_path.replace("\\", "/")
            FileSyncHandler.__createFile(src_path)

    @staticmethod
    def __createFile(src):
        print("create file " + src)

        # get current directory
        directoryPath = getDirectoryPath(src)
        remoteDirectory = FileSyncHandler.__getRemoteDirectory(directoryPath)

        # get new created file
        fileName = getDirectoryOrFileName(src)
        files = {"file": open(src, "rb")}

        request_url = getRequestURL("/data/file")
        request_url += "?directory=" + remoteDirectory["id"]

        headers = getRequestHeaders(True, "")
        response = requests.put(
            url=request_url, files=files, headers=headers)

    @staticmethod
    def __moveFile(src, dest):
        print("TODO move file " + src + " to " + dest)

    @staticmethod
    def deleteFile(event):
        print("delete file: " + event.src_path)

        src_path = event.src_path.replace("\\", "/")
        remoteFile = FileSyncHandler.__getRemoteFile(src_path)

        if remoteFile:
            request_url = getRequestURL("/data/file")
            request_url += "?uuid=" + remoteFile["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)
        else:
            print("ERR: File deletion of " + event.src_path +
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
    def __getRemoteDirectory(path):
        path = removeBaseURL(path, False)

        # search for sync directory by path
        syncDirectories = ServerSettings.getSyncDirectories(False)

        for syncDirectory in syncDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == path:
                return syncDirectory

        return {}
