import requests
from hashlib import sha256
from services.localappmanager import LocalAppManager


def isLoggedIn():
    jwt = LocalAppManager.readLocalJWT()
    headers = {"Authorization": "Bearer {}".format(jwt)}
    response = requests.get(
        "http://localhost:8080/v1/user/test", headers=headers)
    return response.status_code == 200


def register(firstname, lastname, email, password):
    pwHash = hashPassword(password)
    registerData = {"firstname": firstname,
                    "lastname": lastname, "email": email, "pw_hash": pwHash}
    r = requests.post(
        "http://localhost:8080/v1/user/registration", json=registerData)


def login(email, password, openSetingsScreen):
    pwHash = hashPassword(password)
    loginData = {"email": email, "pw_hash": pwHash}
    response = requests.post(
        "http://localhost:8080/v1/user/login", json=loginData)

    if response.status_code != 200:
        return "Login failed: " + response.text

    jwt = response.json()["jwt"]
    LocalAppManager.saveJWTLocally(jwt)
    openSetingsScreen()


def logout(openLoginScreen):
    jwt = LocalAppManager.readLocalJWT()
    headers = {"Authorization": "Bearer {}".format(jwt)}
    response = requests.post(
        "http://localhost:8080/v1/user/logout", headers=headers)
    if response.status_code == 200:
        LocalAppManager.removeJWTLocally()
        openLoginScreen()
        return True

    return False


def hashPassword(string):
    return str(sha256(string.encode('utf-8')).hexdigest())
