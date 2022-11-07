import os


class Worker:

    def start(self):
        # print("start worker")
        syncFolderPath = self.getSyncFolderPath()

        # create sync folder if not exists
        if not os.path.isdir(syncFolderPath):
            os.makedirs(syncFolderPath)

    def getSyncFolderPath(self):
        return "./test/client"
