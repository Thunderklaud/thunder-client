import requests
from watchdog.events import FileSystemEventHandler
from services.localappmanager import LocalAppManager
from services.serversettings import ServerSettings
from config import Config
from utils.folder import removeBaseURL, getFolderName, getFolderPath


class FolderSyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        if event.event_type == "moved":
            src_path = event.src_path.replace("\\", "/")
            dest_path = event.dest_path.replace("\\", "/")
            FolderSyncHandler.__moveFolder(src_path, dest_path)

    @staticmethod
    def __moveFolder(src, dest):
        print("move file from " + src + " to " + dest)
        remote_folder = FolderSyncHandler.__getRemoteFolder(src)

        # if remote folder was found
        if remote_folder:
            old_folder_path = getFolderPath(src)
            new_folder_path = getFolderPath(dest)
            # print(old_folder_path + ":"+new_folder_path)

            old_folder_name = getFolderName(src)
            new_folder_name = getFolderName(dest)
            # print(old_folder_name + ":"+new_folder_name)

            # moved folder into another
            if (old_folder_path != new_folder_path and old_folder_name == new_folder_name):
                print("moved folder")
            else:  # renamed folder
                print("renamed folder")
                jwt = LocalAppManager.readLocalJWT()
                headers = {"Content-Type": "application/json",
                           "Authorization": "Bearer {}".format(jwt)}
                request_url = LocalAppManager.getSetting(
                    "server_url") + Config.API_VERSION + "/data/directory"
                data = {"id": remote_folder["id"], "name": new_folder_name}
                response = requests.patch(
                    url=request_url, json=data, headers=headers)

    @staticmethod
    def __getRemoteFolder(path):
        path = removeBaseURL(path)

        # search for sync folder by path
        syncFolders = ServerSettings.getSyncFolders(False)

        for syncFolder in syncFolders:
            # print(path+":"+syncFolder["path"])
            if "path" in syncFolder and syncFolder["path"] == path:
                return syncFolder

        return {}
