import time
import threading
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.sync_handler.foldersynchandler import FolderSyncHandler
from services.sync_handler.filesynchandler import FileSyncHandler
from services.localappmanager import LocalAppManager
from services.serversettings import ServerSettings
from utils.file import removeBaseURL


class ThunderSyncHandler:

    def __init__(self):
        self.observer = Observer()
        self.observer_directory = LocalAppManager.getSetting(
            "local_sync_folder_path")

    def run(self):
        t1 = threading.Thread(target=self.start)
        t1.start()

    def start(self):
        print("start folder sync")
        event_handler = SyncHandler()

        self.observer.schedule(
            event_handler, self.observer_directory, recursive=True)

        self.observer.daemon = True
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer error")


class SyncHandler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):

        folderHandler = FolderSyncHandler()
        fileHandler = FileSyncHandler()

        # delete files and folders
        if event.event_type == "deleted":
            SyncHandler.__deleteFileOrFolder(event)
            return

        if event.is_directory:
            folderHandler.handle(event)

        if not event.is_directory:
            fileHandler.handle(event)

    @staticmethod
    def __deleteFileOrFolder(event):

        filePath = removeBaseURL(event.src_path, True)
        folderPath = removeBaseURL(event.src_path, False)
        deleteType = 0  # 0 = undefined, 1 = file, 2 = directory
        remoteObject = {}

        # check if remote folder exists
        remoteFolders = ServerSettings.getSyncFolders(False)
        for syncFolder in remoteFolders:
            if "path" in syncFolder and syncFolder["path"] == folderPath:
                deleteType = 2
                remoteObject = syncFolder
                break

        # if path is not an folder => check if its a file
        if "id" not in remoteObject:
            remoteFiles = ServerSettings.getSyncFiles()
            for syncFile in remoteFiles:
                if "path" in syncFile and syncFile["path"] == filePath:
                    deleteType = 1
                    remoteObject = syncFile
                    break

        if deleteType == 1:
            FileSyncHandler.deleteFile(event)
        elif deleteType == 2:
            FolderSyncHandler.deleteFolder(event)
        else:
            print("ERR: undefined delete type")
