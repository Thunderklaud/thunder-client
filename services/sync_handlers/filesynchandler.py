import requests
from watchdog.events import FileSystemEventHandler
from services.server_settings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.file import removeBaseURL, getDirectoryOrFileName, getDirectoryPath, uniqueFilePath


class FileSyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        # handle file RENAME
        if event.event_type == "moved":
            src_path = uniqueFilePath(event.src_path)
            dest_path = uniqueFilePath(event.dest_path)
            FileSyncHandler.__renameFile(src_path, dest_path)

        # handle file CREATE
        if event.event_type == "created":
            src_path = uniqueFilePath(event.src_path)
            FileSyncHandler.createFile(src_path)

        # handle file MODIFY
        if event.event_type == "modified":
            src_path = uniqueFilePath(event.src_path)
            FileSyncHandler.__modifyFile(src_path)

    @staticmethod
    def createFile(src):
        # ThunderSyncHandler.STATUS = 2
        print("[INFO] Create file: " + src)

        # get current directory
        directoryPath = getDirectoryPath(src)
        remoteDirectory = FileSyncHandler.__getRemoteDirectory(directoryPath)

        if remoteDirectory:
            try:
                fileHandle = open(src, "rb")
                files = {"file": fileHandle}

                request_url = getRequestURL("/data/file")
                request_url += "?directory=" + remoteDirectory["id"]

                headers = getRequestHeaders(True, "")
                requests.put(
                    url=request_url, files=files, headers=headers)

                fileHandle.close()
            except FileNotFoundError:
                print(
                    "[ERR] Renamed file to fast. Try to delete and create the file again.")
        else:
            print("[ERR] Remote directory not found: " +
                  directoryPath + ", skip file")

        print("[INFO] Create file done")
        # ThunderSyncHandler.STATUS = 1

    @staticmethod
    def __renameFile(src, dest):
        # ThunderSyncHandler.STATUS = 2
        print("[INFO] Rename file " + src + " to " + dest)

        remoteFile = FileSyncHandler.__getRemoteFile(src)

        if remoteFile:
            newName = getDirectoryOrFileName(dest)
            request_url = getRequestURL("/data/file")

            # body data
            data = {"uuid": remoteFile["id"], "new_name": newName}

            headers = getRequestHeaders()
            requests.patch(
                url=request_url, json=data, headers=headers)

        print("[INFO] Renamed file done.")
        # ThunderSyncHandler.STATUS = 1

    @staticmethod
    def deleteFile(src_path):
        # ThunderSyncHandler.STATUS = 2
        src_path = src_path.replace("\\", "/")
        print("[INFO] Delete file: " + src_path)

        remoteFile = FileSyncHandler.__getRemoteFile(src_path)

        if remoteFile:
            request_url = getRequestURL("/data/file")
            request_url += "?uuid=" + remoteFile["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)

            if response.status_code == 404:
                print("[ERR]: file not on remote file system")
        else:
            print("[ERR] File deletion of " + src_path +
                  " not possible, not found on the server")

        print("[INFO] Delete file done")
        # ThunderSyncHandler.STATUS = 1

    @staticmethod
    def __modifyFile(src_path):
        # ThunderSyncHandler.STATUS = 2
        src_path = src_path.replace("\\", "/")
        print("[INFO] Modify file (delete and create): " + src_path)

        # delete old file
        FileSyncHandler.deleteFile(src_path)

        # create new file
        FileSyncHandler.createFile(src_path)

        print("[INFO] Modify file (delete and create) done")
        # ThunderSyncHandler.STATUS = 1

    @staticmethod
    def __getRemoteFile(path):
        path = removeBaseURL(path, True)

        remoteFiles = ServerSettings.getSyncFiles()

        for remotePath in remoteFiles:
            if "path" in remotePath and remotePath["path"] == path:
                return remotePath

        return {}

    # same as __getRemoteDirectory() in DirectorySyncHandler
    @staticmethod
    def __getRemoteDirectory(dir_path):
        dir_path = removeBaseURL(dir_path, False)

        # search for sync directory by path
        syncDirectories = ServerSettings.getSyncDirectories(False, True)
        print(syncDirectories)

        for syncDirectory in syncDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == dir_path:
                return syncDirectory

        return {}
