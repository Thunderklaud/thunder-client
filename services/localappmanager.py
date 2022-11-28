from pathlib import Path
import os


class LocalAppManager():

    @staticmethod
    def getLocalAppPath():
        home = str(Path.home())
        appDir = "/.thunderklaud/"
        return home + appDir

    @staticmethod
    def getLocalJWTPath():
        return LocalAppManager.getLocalAppPath() + "jwt"

    @staticmethod
    def createLocalAppPathIfNotExists():
        localAppPath = LocalAppManager.getLocalAppPath()
        if not os.path.isdir(localAppPath):
            os.makedirs(localAppPath)

    @staticmethod
    def saveJWTLocally(jwt):
        localJWTPath = LocalAppManager.getLocalJWTPath()

        with open(localJWTPath, 'w') as f:
            f.write(jwt)

    @staticmethod
    def readLocalJWT():
        localJWTPath = LocalAppManager.getLocalJWTPath()
        if not os.path.exists(localJWTPath):
            return ""

        jwtFile = open(localJWTPath, "r")
        return jwtFile.read()

    def getSetting(name):
        if name == "server_url":
            return "http://localhost:8080/"
        if name == "local_sync_folder_path":
            return "./test/client/"

    def removeJWTLocally():
        localJWTPath = LocalAppManager.getLocalJWTPath()
        os.remove(localJWTPath)
