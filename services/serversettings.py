import requests
from services.localappmanager import LocalAppManager
from config import Config


class ServerSettings():

    @staticmethod
    def getSyncFolders():
        jwt = LocalAppManager.readLocalJWT()
        headers = {"Conent-Type": "application/json",
                   "Authorization": "Bearer {}".format(jwt)}
        requestURL = LocalAppManager.getSetting(
            "server_url") + Config.API_VERSION + "/data/directory"
        data = {"name": "First folder"}

        response = requests.get(url=requestURL, data=data, headers=headers)
        # print(response.text)
