from services.localappmanager import LocalAppManager
from config import Config


def getRequestURL(route):
    return LocalAppManager.getSetting(
        "serverURL") + Config.API_VERSION + route


def getRequestHeaders(auth=True, contentType="application/json"):
    jwt = LocalAppManager.readLocalJWT()
    headers = {}

    if contentType:
        headers = {"Content-Type": contentType}

    if auth:
        headers["Authorization"] = "Bearer {}".format(jwt)

    return headers
