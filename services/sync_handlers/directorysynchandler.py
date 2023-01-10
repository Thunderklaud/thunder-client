import requests
from watchdog.events import FileSystemEventHandler
from services.server_settings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.file import getDirectoryOrFileName, getDirectoryPath, uniqueDirectoryPath, removeBaseURL


class DirectorySyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        # handle directory MOVE/RENAME
        if event.event_type == "moved":
            src_path = uniqueDirectoryPath(event.src_path)
            dest_path = uniqueDirectoryPath(event.dest_path)
            DirectorySyncHandler.__moveDirectory(src_path, dest_path)

        # handle directory CREATE
        if event.event_type == "created":
            src_path = uniqueDirectoryPath(event.src_path)
            DirectorySyncHandler.__createDirectory(src_path)

    @staticmethod
    def __createDirectory(src):
        from services.thundersynchandler import ThunderSyncHandler

        ThunderSyncHandler.STATUS = 2
        print("[INFO] Create directory " + src)

        directoryName = getDirectoryOrFileName(src)
        directoryPath = getDirectoryPath(src)

        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(
            directoryPath)
        print("remote dir: ")
        print(remoteDirectory)

        # set parent id empty or get parent id if sub folder
        parentId = ""
        if remoteDirectory:
            parentId = remoteDirectory["id"]

        request_url = getRequestURL("/data/directory")
        headers = getRequestHeaders()
        data = {"parent_id": parentId, "name": directoryName}
        requests.post(
            url=request_url, json=data, headers=headers)

        print("[INFO] Create directory done")
        ThunderSyncHandler.STATUS = 1

    @staticmethod
    def __moveDirectory(src, dest):
        from services.thundersynchandler import ThunderSyncHandler

        ThunderSyncHandler.STATUS = 2
        print("[INFO] Move/Rename directory from " + src + " to " + dest)
        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(src)

        # if remote directory was found
        if remoteDirectory:
            # TODO: this CANNOT work!!
            directoryPath = getDirectoryPath(src)
            directoryPath = getDirectoryPath(dest)
            # print(directoryPath + ":"+directoryPath)

            directoryName = getDirectoryOrFileName(src)
            directoryName = getDirectoryOrFileName(dest)
            # print(directoryName + ":"+directoryName)

            # moved directory into another
            if (directoryPath != directoryPath and directoryName == directoryName):
                # TODO
                print("TODO: move directory, not implemented yet")
            else:  # renamed directory
                request_url = getRequestURL("/data/directory")
                headers = getRequestHeaders()
                data = {"id": remoteDirectory["id"], "name": directoryName}
                requests.patch(
                    url=request_url, json=data, headers=headers)

        print("[INFO] Move/Rename directory done")
        ThunderSyncHandler.STATUS = 1

    @staticmethod
    def deleteDirectory(src_path):
        from services.thundersynchandler import ThunderSyncHandler

        ThunderSyncHandler.STATUS = 2
        src_path = src_path.replace("\\", "/")
        print("[INFO] Delete directory: " + src_path)

        remoteDirectory = DirectorySyncHandler.__getRemoteDirectory(src_path)

        if remoteDirectory:
            request_url = getRequestURL("/data/directory")
            request_url += "?id=" + remoteDirectory["id"]

            headers = getRequestHeaders()
            response = requests.delete(
                url=request_url, json={}, headers=headers)
        else:
            print("[ERR] Deletion of " + src_path +
                  " not possible. Directory not found on server")

        print("[INFO] Delete directory done")
        ThunderSyncHandler.STATUS = 1

    # same as __getRemoteDirectory() in FileSyncHandler
    @staticmethod
    def __getRemoteDirectory(path):
        path = removeBaseURL(path, False)

        # search for sync directory by path
        syncDirectories = ServerSettings.getSyncDirectories(False)

        for syncDirectory in syncDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == path:
                return syncDirectory

        return {}
