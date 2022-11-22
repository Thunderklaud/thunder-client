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
    pw_hash = hashPassword(password)
    registerData = {"firstname": firstname,
                    "lastname": lastname, "email": email, "pw_hash": pw_hash}
    r = requests.post(
        "http://localhost:8080/v1/user/registration", json=registerData)
    print(r.json())


def login(email, password, openSetingsScreen):
    pw_hash = hashPassword(password)
    loginData = {"email": email, "pw_hash": pw_hash}
    response = requests.post(
        "http://localhost:8080/v1/user/login", json=loginData)

    jsonResponse = response.json()
    if jsonResponse["status"] == False:
        return "Login failed: " + str(jsonResponse["error"])

    print(response.json())
    jwt = response.json()["result"]["jwt"]
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
    
