import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.sync_handlers.directorysynchandler import DirectorySyncHandler
from services.sync_handlers.filesynchandler import FileSyncHandler
from services.localappmanager import LocalAppManager
from services.server_settings import ServerSettings
from utils.file import removeBaseURL, uniqueFilePath, uniqueDirectoryPath


class ThunderSyncHandler:

    # global variable to set the observers state (0 = offline, 1 = running, 2 = syncing)
    STATUS = 0

    def __init__(self):
        self.observer = Observer()
        self.observer_directory = LocalAppManager.getSetting(
            "localSyncFolderPath")

    # Start observer in new thread
    def run(self):
        t1 = threading.Thread(target=self.start)
        t1.start()

    def start(self):
        print("[INFO] Starting watchdog synchronisation for " +
              self.observer_directory + "...")
        ThunderSyncHandler.STATUS = 1
        event_handler = SyncHandlerHelper()

        self.observer.schedule(
            event_handler, self.observer_directory, recursive=True)

        self.observer.start()
        try:
            while ThunderSyncHandler.STATUS != 0:
                time.sleep(3)
        except:
            self.observer.stop()
            print("ThunderSyncHandler Observer error")


class SyncHandlerHelper(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):

        # delete files and directories
        if event.event_type == "deleted":
            SyncHandlerHelper.__deleteFileOrDirectory(event)
            return

        # handle other directory events
        if event.is_directory:
            DirectorySyncHandler().handle(event)
        else:   # handle other file events
            FileSyncHandler().handle(event)

    @staticmethod
    def __deleteFileOrDirectory(event):
        ThunderSyncHandler.STATUS = 2

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
            src_path = uniqueFilePath(event.src_path)
            FileSyncHandler.deleteFile(src_path)
        elif deleteType == 2:
            src_path = uniqueDirectoryPath(event.src_path)
            DirectorySyncHandler.deleteDirectory(src_path)
        else:
            # handles file move (watchdog is so bad :c)
            src_path = uniqueFilePath(event.src_path)
            FileSyncHandler.deleteFile(src_path)

    ThunderSyncHandler.STATUS = 1
