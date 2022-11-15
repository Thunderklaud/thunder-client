from pathlib import Path
import os


def isLoggedIn():
    # TODO: Check if local JWT is valid
    return False


def getLocalAppPath():
    home = str(Path.home())
    appDir = "/.thunderklaud/"
    return home + appDir


def createLocalAppPathIfNotExists():
    localAppPath = getLocalAppPath()
    if not os.path.isdir(localAppPath):
        os.makedirs(localAppPath)


def saveJWTLocally(jwt):
    localJWTPath = getLocalAppPath() + "jwt"

    with open(localJWTPath, 'w') as f:
        f.write(jwt)
