import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.sync_handler.foldersynchandler import FolderSyncHandler
from services.localappmanager import LocalAppManager


class FolderSyncer:

    def __init__(self):
        self.observer = Observer()
        self.observer_directory = LocalAppManager.getSetting(
            "local_sync_folder_path")

    def run(self):
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
        if event.is_directory:
            folderHandler = FolderSyncHandler()
            folderHandler.handle(event)
