import os


class Worker:

    localSyncFolderPath = "./test/client"

    def start(self):
        # print("start worker")
        syncFolderPath = self.getSyncFolderPath()

        # create sync folder if not exists
        if not os.path.isdir(syncFolderPath):
            os.makedirs(syncFolderPath)

    @staticmethod
    def getSyncFolderPath():
        return Worker.localSyncFolderPath

    @staticmethod
    def setLocalSyncFolderPath(path):
        Worker.localSyncFolderPath = path
