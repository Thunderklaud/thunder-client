import requests
from hashlib import sha256
from services.localappmanager import LocalAppManager
from services.thundersynchandler import ThunderSyncHandler
from services.startup_syncer import StartupSyncer
from utils.request import getRequestHeaders, getRequestURL


def isLoggedIn():
    headers = getRequestHeaders()
    requestURL = getRequestURL("/user/test")
    response = requests.get(url=requestURL, headers=headers)

    return response.status_code == 200


def register(firstname, lastname, email, password):
    pwHash = hashPassword(password)

    requestURL = getRequestURL("/user/registration")
    registerData = {"firstname": firstname,
                    "lastname": lastname, "email": email, "pw_hash": pwHash}
    requests.post(url=requestURL, json=registerData)


def login(email, password, openSetingsScreen):
    pwHash = hashPassword(password)

    requestURL = getRequestURL("/user/login")
    loginData = {"email": email, "pw_hash": pwHash}
    response = requests.post(url=requestURL, json=loginData)

    # handle server error response
    if response.status_code != 200:
        return "Login failed: " + response.text

    jsonResponse = response.json()

    # handle unknown user
    if "status" in jsonResponse and not jsonResponse.status:
        return "Login failed: " + response.error

    # handle jwt and open settings window
    jwt = response.json()["jwt"]
    LocalAppManager.saveJWTLocally(jwt)
    openSetingsScreen()


def logout(openLoginScreen):
    headers = getRequestHeaders()
    requestURL = getRequestURL("/user/logout")
    response = requests.post(url=requestURL, headers=headers)

    # remove local jwt and open login window
    if response.status_code == 200:
        LocalAppManager.removeJWTLocally()
        openLoginScreen()
        return True

    return False


def hashPassword(string):
    return str(sha256(string.encode('utf-8')).hexdigest())


def doAfterLoginActions():
    if isLoggedIn():
        startupSyncer = StartupSyncer()
        startupSyncer.start()

        sync_handler = ThunderSyncHandler()
        sync_handler.run()
