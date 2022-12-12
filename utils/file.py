from services.localappmanager import LocalAppManager


def remoteFileOrDirectoryExists(directories, path):
    for directory in directories:
        if "path" in directory and directory["path"] == path:
            return True

    return False


def uniqueDirectoryPath(path):
    if path == "":
        return "/"

    path = path.replace("\\", "/")
    path = path.replace("//", "/")

    trailingSlash = path[-1] == "/"
    beginningSlash = path[0] == "/"
    beginningDot = path[0] == "."

    if not trailingSlash:
        path = path + "/"

    if not beginningSlash and not beginningDot:
        path = "/" + path

    # TODO: remove double slashes

    return path


def uniqueFilePath(path):
    if path == "":
        return "/"

    path = path.replace("\\", "/")
    path = path.replace("//", "/")

    beginningDot = path[0] == "."
    beginningSlash = path[0] == "/"

    if not beginningSlash and not beginningDot:
        path = "/" + path

    # TODO: remove double slashes

    return path


def removeBaseURL(path, isFile):
    syncDirectoryPath = LocalAppManager.getSetting(
        "local_sync_folder_path")
    localPathLength = len(syncDirectoryPath)
    pathLength = len(path)
    path = path[localPathLength:pathLength]

    if isFile:
        return uniqueFilePath(path)
    return uniqueDirectoryPath(path)


def getDirectoryName(path):
    position = path.rfind("/") + 1  # + 1 to remove the / at the begin
    string_length = len(path)

    return path[position:string_length]


def getDirectoryPath(path):
    position = path.rfind("/")

    return path[0:position]
