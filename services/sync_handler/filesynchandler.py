import requests
from watchdog.events import FileSystemEventHandler
from services.serversettings import ServerSettings
from utils.request import getRequestURL, getRequestHeaders
from utils.folder import removeBaseURL, getFolderName, getFolderPath


class FileSyncHandler(FileSystemEventHandler):

    @staticmethod
    def handle(event):

        print(event)
        print(event.event_type)

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

    @staticmethod
    def __moveFile(src, dest):
        print("move file " + src + " to " + dest)
