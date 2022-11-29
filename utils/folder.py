from services.localappmanager import LocalAppManager


def remoteFolderExists(folders, path):
    for folder in folders:
        if "path" in folder and folder["path"] == path:
            return True

    return False


def uniqieFolderPath(path):
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

    # remove double slashes

    return path


def removeBaseURL(path):
    syncFolderPath = LocalAppManager.getSetting(
        "local_sync_folder_path")
    localPathLength = len(syncFolderPath)
    pathLength = len(path)
    path = path[localPathLength:pathLength]

    return uniqieFolderPath(path)


def getFolderName(path):
    position = path.rfind("/") + 1  # + 1 to remove the / at the begin
    string_length = len(path)

    return path[position:string_length]


def getFolderPath(path):
    position = path.rfind("/")

    return path[0:position]
