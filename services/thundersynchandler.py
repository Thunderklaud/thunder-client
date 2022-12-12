import time
import threading
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.sync_handler.directorysynchandler import DirectorySyncHandler
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
        print("[INFO] Starting synchronisation for " +
              self.observer_directory)
        event_handler = SyncHandler()

        self.observer.schedule(
            event_handler, self.observer_directory, recursive=True)

        self.observer.daemon = True
        self.observer.start()
        try:
            while True:
                time.sleep(3)
        except:
            self.observer.stop()
            print("Observer error")


class SyncHandler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print(event)

        directoryHandler = DirectorySyncHandler()
        fileHandler = FileSyncHandler()

        # delete files and directories
        if event.event_type == "deleted":
            SyncHandler.__deleteFileOrDirectory(event)
            return

        if event.is_directory:
            directoryHandler.handle(event)

        if not event.is_directory:
            fileHandler.handle(event)

    @staticmethod
    def __deleteFileOrDirectory(event):

        filePath = removeBaseURL(event.src_path, True)
        directoryPath = removeBaseURL(event.src_path, False)
        deleteType = 0  # 0 = undefined, 1 = file, 2 = directory
        remoteObject = {}

        # check if remote directory exists
        remoteDirectories = ServerSettings.getSyncDirectories(False)
        for syncDirectory in remoteDirectories:
            if "path" in syncDirectory and syncDirectory["path"] == directoryPath:
                deleteType = 2
                remoteObject = syncDirectory
                break

        # if path is not an directory => check if its a file
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
            DirectorySyncHandler.deleteDirectory(event)
        else:
            print("ERR: undefined delete type")
