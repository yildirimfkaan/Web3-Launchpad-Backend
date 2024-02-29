from datetime import datetime
import json
import logging
import inspect
import requests
import os

from sqlalchemy import false

logging.basicConfig(
    filename="tests/logs/" + str(datetime.now()) + ".log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

TEST_URL = os.getenv("test_api_address")


def test_signup():
    signup_info = json.load(open("tests/json/signup.json", "r"))
    response = requests.post(
        TEST_URL + "/signup",
        data=signup_info,
    )
    user_reponse = response.json()
    activate_user(user_reponse["activation_token"], user_reponse["is_active"])
    controller(response, 200)


def activate_user(token, activation_code):
    response = requests.post(
        TEST_URL + "/activate/",
        json={"token": token, "activation_code": activation_code},
    )
    controller(response, 200)


def test_login():
    login_info = json.load(open("tests/json/login.json", "r"))
    response = requests.post(
        TEST_URL + "/login",
        data=login_info,
    )
    controller(response, 200)
    token = json.loads(response.text)
    with open("tests/token.txt", "w") as f:
        f.write(token["access_token"])


def test_create_project():
    createProject = open("tests/json/createProject.json")
    createProject = json.load(createProject)
    response = requests.post(
        TEST_URL + "/projects",
        headers=get_token(),
        json=createProject,
    )
    controller(response)


def test_error_create_project_without_token():
    createProject = open("tests/json/createProject.json")
    createProject = json.load(createProject)
    del createProject["token"]["name"]
    response = requests.post(
        TEST_URL + "/projects",
        headers=get_token(),
        json=createProject,
    )
    controller(response, 422)

    del createProject["token"]
    response = requests.post(
        TEST_URL + "/projects",
        headers=get_token(),
        json=createProject,
    )
    controller(response, 422)


def test_error_create_project_without_project_vars():
    createProject = open("tests/json/createProject.json")
    createProject = json.load(createProject)
    del createProject["name"]
    response = requests.post(
        TEST_URL + "/projects",
        headers=get_token(),
        json=createProject,
    )
    controller(response, 422)


def test_create_project_without_social():
    createProject = open("tests/json/createProject.json")
    createProject = json.load(createProject)
    del createProject["social"]
    response = requests.post(
        TEST_URL + "/projects",
        headers=get_token(),
        json=createProject,
    )
    controller(response, 200)


def test_add_project_image():
    response = requests.put(
        TEST_URL + "/projects/1/image",
        files={"image": open("tests/test_image.jpeg", "rb"),"logo": open("tests/test_image.jpeg", "rb")},
    )
    controller(response, 200)


def test_get_project_image():
    response = requests.get(TEST_URL + "/projects/1/image")
    controller(response, 200)

def test_get_project_logo():
    response = requests.get(TEST_URL + "/projects/1/logo")
    controller(response, 200)

def test_get_projects():
    response = requests.get(TEST_URL + "/projects")
    controller(response)


def test_get_project_by_id():
    response = requests.get(TEST_URL + "/projects/1")
    controller(response)


def test_error_get_project_by_id():
    response = requests.get(TEST_URL + "/projects/3")
    controller(response, 400)


def test_update_project():
    updateProject = open("tests/json/updateProject.json")
    updateProject = json.load(updateProject)
    response = requests.put(
        TEST_URL + "/projects/1",
        headers=get_token(),
        json=updateProject,
    )
    controller(response)


def test_error_update_project():
    updateProject = open("tests/json/updateProject.json")
    updateProject = json.load(updateProject)
    updateProject["name"] = None
    response = requests.put(
        TEST_URL + "/projects/1",
        headers=get_token(),
        json=updateProject,
    )
    controller(response, 400)


def test_get_token():
    response = requests.get(TEST_URL + "/tokens/1")
    controller(response)


def test_error_get_token():
    response = requests.get(TEST_URL + "/tokens/3")
    controller(response, 400)


def test_create_token():
    createToken = open("tests/json/createToken.json")
    createToken = json.load(createToken)
    response = requests.post(
        TEST_URL + "/tokens",
        headers=get_token(),
        json=createToken,
    )
    controller(response)


def test_error_create_token():
    createToken = open("tests/json/updateToken.json")
    createToken = json.load(createToken)
    del createToken["name"]
    response = requests.post(
        TEST_URL + "/tokens",
        headers=get_token(),
        json=createToken,
    )
    controller(response, 422)


def test_update_token():
    updateToken = open("tests/json/updateToken.json")
    updateToken = json.load(updateToken)
    response = requests.put(
        TEST_URL + "/tokens/3",
        headers=get_token(),
        json=updateToken,
    )
    controller(response)


def test_error_update_token():
    updateToken = open("tests/json/updateToken.json")
    updateToken = json.load(updateToken)
    updateToken["name"] = None
    response = requests.put(
        TEST_URL + "/tokens/1",
        headers=get_token(),
        json=updateToken,
    )
    controller(response)


def test_get_socials():
    response = requests.get(TEST_URL + "/project/1/socials")
    controller(response)

def test_error_get_socials():
    response = requests.get(TEST_URL + "/project/3/socials")
    controller(response, 400)

def test_create_social():
    createSocials = open("tests/json/createSocial.json")
    createToken = json.load(createSocials)
    response = requests.post(
        TEST_URL + "/project/2/socials",
        headers=get_token(),
        json=createToken,
    )
    controller(response)

def test_update_social():
    updateDetail = open("tests/json/updateSocial.json")
    updateDetail = json.load(updateDetail)
    response = requests.put(
        TEST_URL + "/project/1/socials",
        headers=get_token(),
        json=updateDetail,
    )
    controller(response)


def test_error_update_socials():
    updateDetail = open("tests/json/updateSocial.json")
    updateDetail = json.load(updateDetail)
    response = requests.put(
        TEST_URL + "/project/3/socials",
        headers=get_token(),
        json=updateDetail,
    )
    controller(response, 400)



def test_get_round():
    response = requests.get(TEST_URL + "/project/1/round")
    controller(response)


def test_error_get_round():
    response = requests.get(TEST_URL + "/project/3/round")
    controller(response, 400)

def test_create_round():
    rounds = ["registration","validation","staking","publicsale","privatesale"]
    createRound = open("tests/json/createRound.json")
    createRound = json.load(createRound)
    for round in rounds:
        response = requests.post(
            TEST_URL + "/project/1/round/" + round,
            headers=get_token(),
            json=createRound,
        )
        controller(response = response, explanation = str(round))

def test_update_round():
    rounds = ["registration","validation","staking","publicsale","privatesale"]
    updateRound = open("tests/json/createRound.json")
    updateRound = json.load(updateRound)
    for round in rounds:
        response = requests.put(
            TEST_URL + "/project/1/round/" + round,
            headers=get_token(),
            json=updateRound,
        )
        controller(response = response, explanation = str(round))


def test_password_reset():
    new_password = open("tests/json/passwordRecovery.json")
    new_password = json.load(new_password)
    response = requests.post(
        TEST_URL + "/password-recovery", data={"email": "test_mail@test.com"}
    )
    controller(response, 200)
    password_token = json.loads(response.text)
    new_password["token"] = password_token["token"]
    response = requests.post(
        TEST_URL + "/reset-password/",
        json=new_password,
    )
    controller(response, 200)


def test_user_profile():
    response = requests.get(
        TEST_URL + "/user/profile",
        headers=get_token(),
    )
    controller(response)


def test_kyc():
    updateKyc = open("tests/json/updateKyc.json")
    updateKyc = json.load(updateKyc)
    response = requests.put(
        TEST_URL + "/user/100000000/kyc",
        headers=get_token(),
        json=updateKyc,
    )
    controller(response)

def test_bsc():
    get_bsc = open("tests/json/getBscApi.json")
    get_bsc = json.load(get_bsc)
    response = requests.post(
        TEST_URL + "/bsc",
        headers=get_token(),
        json=get_bsc,
    )
    print(response.json())

    bsc_status = response.json()["status"]
    assert bsc_status == "1"
    controller(response)


def test_drop_key():
    # drop_database(SQLALCHEMY_DATABASE_URL)
    os.remove("tests/token.txt")


def controller(response, expected_code=200, explanation = ""):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    if response.status_code != expected_code:
        logging.error(
            (calframe[1][3]) + " : " + explanation + " : "+ str(response.status_code) + " : " + response.text
        )
    assert response.status_code == expected_code
    logging.info(
        (calframe[1][3]) + " : " + str(response.status_code) + " : " + response.text
    )

def get_token():
    f = open("tests/token.txt", "r")
    token = f.read()
    headers = {"Authorization": "Bearer {}".format(token)}
    return headers
