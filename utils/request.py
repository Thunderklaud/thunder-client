from services.localappmanager import LocalAppManager
from config import Config


def getRequestURL(route):
    return LocalAppManager.getSetting(
        "server_url") + Config.API_VERSION + route


def getRequestHeaders(auth=True):
    jwt = LocalAppManager.readLocalJWT()
    headers = {"Content-Type": "application/json"}

    if auth:
        headers["Authorization"] = "Bearer {}".format(jwt)

    return headers
