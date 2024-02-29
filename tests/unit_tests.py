from datetime import datetime
import json
import logging
import inspect
import requests
import os
from fastapi import HTTPException, status, Depends, Body
# import auth
from .API.auth import get_current_active_user, get_current_user, get_current_active_superuser

# from dotenv import load_dotenv
# load_dotenv()
# logging.basicConfig(
#     filename="logs/" + str(datetime.now()) + ".log",
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s:%(message)s",
#     datefmt="%m/%d/%Y %I:%M:%S %p",
# )

TEST_URL = os.getenv("test_api_address")


# def test_signup():
#     signup_info = json.load(open("tests/json/signup.json", "r"))
#     response = requests.post(
#         TEST_URL + "/signup",
#         data=signup_info,
#     )
#     controller(response, 200)

def test_login():
    login_info = json.load(open("tests/json/login.json", "r"))
    response = requests.post(
        TEST_URL + "/login",
        data=login_info,
    )
    controller(response, 200)
    token = json.loads(response.text)
    with open("token.txt", "w") as f:
        f.write(token["access_token"])


def test_current_user():
    with open("token.txt", "r") as f:
        token = f.read()
    print(token)
    response = Depends(get_current_user(token = token))
    print(response)


# def test_active_user():
#     get_current_active_user()
#     createProject = open("json/createProject.json")
#     createProject = json.load(createProject)
#     response = requests.post(
#         TEST_URL + "/projects",
#         headers=get_token(),
#         json=createProject,
#     )
#     controller(response)


# def test_super_user():
#     createProject = open("json/createProject.json")
#     createProject = json.load(createProject)
#     del createProject["project_name"]
#     response = requests.post(
#         TEST_URL + "/projects",
#         headers=get_token(),
#         json=createProject,
#     )
#     controller(response, 422)




# def test_drop_key():
#     # drop_database(SQLALCHEMY_DATABASE_URL)
#     os.remove("token.txt")


def controller(response, expected_code=200):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    # if response.status_code != expected_code:
    #     logging.error(
    #         (calframe[1][3]) + " : " + str(response.status_code) + " : " + response.text
    #     )
    assert response.status_code == expected_code
    # logging.info(
    #     (calframe[1][3]) + " : " + str(response.status_code) + " : " + response.text
    # )


def get_token():
    f = open("token.txt", "r")
    token = f.read()
    headers = {"Authorization": "Bearer {}".format(token)}
    return headers
