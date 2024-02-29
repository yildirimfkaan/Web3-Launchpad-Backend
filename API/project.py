from datetime import datetime
import io
import os
import json
import requests
import models, schemas
from typing import Union
from fastapi import File, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
import sqlalchemy
from sqlalchemy.orm import Session
import subprocess

from app import app, get_db
from auth import (
    get_current_active_superuser,
    get_current_user,
    get_current_active_user,
    get_current_user_email,
)
from database import API_CLIENT, DB_NAME
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException

hapikey = os.getenv("hubspot_api_key")
haccesstoken = os.getenv("hubspot_access_token")
chains = json.load(open('contracts/chains.json'))

def create_item(
    cls: models.Base, cls_parameters: dict, current_user, db: Session = Depends(get_db)
):
    cls_parameters["cuser"] = int(current_user.id)
    cls_parameters["uuser"] = int(current_user.id)
    try:
        item = cls(**cls_parameters)
        db.add(item)
        db.flush()
        item_as_json = jsonable_encoder(item)
        return None, item_as_json
    except Exception as e:
        return (
            JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": f"create_item_error: could not create {cls.__tablename__}, {e}"
                },
            ),
            None,
        )


def get_db_object_by_id(cls: models.Base, id: int, db: Session = Depends(get_db)):
    query = db.query(cls).filter(cls.id == id)
    try:
        db_obj = query.one()
    except sqlalchemy.exc.NoResultFound:
        return (
            JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"{cls.__tablename__} {id} not found"},
            ),
            query,
            None,
        )
    return None, query, db_obj


@app.put("/projects/{id}/image", tags=["image"])
def project_image(
    id: int,
    image: Union[bytes, None] = File(default=None),
    logo: Union[bytes, None] = File(default=None),
    db: Session = Depends(get_db),
):
    if not image or not logo:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "No file sent"},
        )
    error, project_query, _ = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    new_image = models.ProjectImage(**{"image": image, "logo": logo})
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    project_query.update({"image_id": new_image.id})
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "project images added"}
    )


@app.get("/projects/{id}/image", tags=["image"])
def project_image(id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(models.Project).filter(models.Project.id == id).one()
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"project {id} does not exist."},
        )
    try:
        project_image = project.image.image
        return StreamingResponse(io.BytesIO(project_image), media_type="image/png")
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"project {id} does not have an image."},
        )


@app.get("/projects/{id}/logo", tags=["image"])
def project_image(id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(models.Project).filter(models.Project.id == id).one()
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"project {id} does not exist."},
        )
    try:
        project_logo = project.image.logo
        return StreamingResponse(io.BytesIO(project_logo), media_type="image/png")
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"project {id} does not have a logo."},
        )


@app.get("/projects", tags=["project"])
def get_project(db: Session = Depends(get_db)):
    try:
        project = db.query(models.Project).all()
        json_project = jsonable_encoder(project)
        return JSONResponse(status_code=status.HTTP_200_OK, content=json_project)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)}
        )


@app.get("/projects/{id}", tags=["project"])
async def get_project_by_id(id: int, db: Session = Depends(get_db)):
    error, _, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error
    if "Test" not in DB_NAME:
        current_user_email = await get_current_user_email()
        if current_user_email is not None:
            url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            headers = {
                "content-type": "application/json",
                "Authorization": "Bearer {}".format(
                    "pat-eu1-5cfb9752-5d88-4f17-aa23-fde227c63ef4"
                ),
            }
            data = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "value": current_user_email,
                                "propertyName": "email",
                                "operator": "EQ",
                            }
                        ]
                    }
                ],
                "properties": ["message"],
                "limit": 1,
                "after": 0,
            }
            r = requests.post(url=url, headers=headers, data=json.dumps(data))
            results = r.json()["results"]
            contact_id = results[0]["id"]
            message = results[0]["properties"]["message"]
            if message is None:
                properties = {
                    "message": str(id),
                }
            else:
                values = message.split(",")
                values.append(str(id))
                values = list(set(values))
                properties = {
                    "message": ",".join(values),
                }
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            try:
                api_response = API_CLIENT.crm.contacts.basic_api.update(
                    contact_id=contact_id,
                    simple_public_object_input=simple_public_object_input,
                )
            except ApiException as e:
                print("Exception when calling basic_api->update: %s\n" % e)
    project.token
    project.token.presale_contract
    project.token.staking_contract
    json_project = jsonable_encoder(project)
    round = "round_"
    is_round = False
    for r in ["registration", "validation", "staking", "privatesale", "publicsale"]:
        if json_project[round + r] is not None:
            is_round = True
            round_time = json_project[round + r]["end_date"][:-6]
            round_time = datetime.fromisoformat(round_time)

            if datetime.now() < round_time:
                json_project["active_round"] = r.capitalize()
                timeleft = round_time - datetime.now()
                days, seconds = timeleft.days, timeleft.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                if days == 0 and hours == 0:
                    json_project["round_time_left"] = str(minutes) + " Minutes"
                elif days == 0:
                    json_project["round_time_left"] = str(hours) + " Hours"
                else:
                    json_project["round_time_left"] = str(days) + " Days "

                break
    if not is_round:
        round_time = json_project[round + "sale"]["end_date"][:-6]
        round_time = datetime.fromisoformat(round_time)
        if datetime.now() > round_time:
            json_project["active_round"] = "Sale Ended"
            json_project["round_time_left"] = "Sale Ended"
        else:
            json_project["active_round"] = "Sale"
            timeleft = round_time - datetime.now()
            days, seconds = timeleft.days, timeleft.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            if days == 0 and hours == 0:
                json_project["round_time_left"] = str(minutes) + " Minutes"
            elif days == 0:
                json_project["round_time_left"] = str(hours) + " Hours"
            else:
                json_project["round_time_left"] = str(days) + " Days "
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_project)


@app.post("/projects", tags=["project"])
def create_project(
    project_in: schemas.ProjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    project_dict = project_in.dict()

    social_dict = project_dict["social"]
    del project_dict["social"]
    if social_dict:  # social can be empty
        error, new_social = create_item(models.Social, social_dict, current_user, db)
        if error:
            return error
        project_dict["social_id"] = new_social["id"]

    round_sale_dict = project_dict["round_sale"]

    round_sale_dict["round_type"] = "round_sale"
    del project_dict["round_sale"]
    error, new_round_sale = create_item(models.Round, round_sale_dict, current_user, db)
    if error:
        return error
    project_dict["round_sale_id"] = new_round_sale["id"]

    token_dict = project_dict["token"]
    del project_dict["token"]
    create_token_response = create_token(
        schemas.TokenCreateSchema(**token_dict), db, current_user, True
    )
    if create_token_response.status_code != status.HTTP_200_OK:
        return create_token_response
    new_token = json.loads(create_token_response.body)
    project_dict["token_id"] = new_token["id"]
    dt_now = datetime.now()
    sale_start = round_sale_dict["start_date"].replace(tzinfo=None)
    sale_end = round_sale_dict["end_date"].replace(tzinfo=None)
    if dt_now > sale_start and dt_now < sale_end:
        project_dict["is_active"] = "active"
    elif dt_now < sale_start:
        project_dict["is_active"] = "incoming"
    else:
        project_dict["is_active"] = "completed"

    error, new_project = create_item(models.Project, project_dict, current_user, db)
    if error:
        return error
    db.commit()
    command = (
        "python /unopad/API/update_crontab.py "
        + str(new_project["id"])
        + " "
        + "completed"
    )
    date_time_str = sale_end.strftime("%H:%M %m/%d/%Y")
    subprocess.run(["at", date_time_str], input=command, encoding="utf-8")
    return JSONResponse(status_code=status.HTTP_200_OK, content=new_project)


@app.put("/projects/{id}", tags=["project"])
def update_project(
    id: int,
    project_in: schemas.ProjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, is_owner = check_authorization(id, current_user, db, models.Project, "cuser")
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    error, project_query, _ = get_db_object_by_id(models.Project, id, db)
    if error:
        return error
    project_request = project_in.dict(exclude_unset=True)

    try:
        project_request["uuser"] = current_user.id
        project_query.update(project_request)
        db.commit()
        json_project = jsonable_encoder(project_request)
        return JSONResponse(status_code=status.HTTP_200_OK, content=json_project)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


# TOKENS PART--------------------------------------------------
@app.get("/tokens", tags=["token"])
def get_token(db: Session = Depends(get_db)):
    token = db.query(models.Token).all()
    json_token = jsonable_encoder(token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_token,
    )


@app.get("/tokens/{id}", tags=["token"])
def get_token_by_id(id: int, db: Session = Depends(get_db)):
    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    token.presale_contract
    token.staking_contract

    json_token = jsonable_encoder(token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_token,
    )


@app.post("/tokens", tags=["token"])
def create_token(
    token_in: schemas.TokenCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    from_func: bool = False,
):
    token_dict = token_in.dict()

    staking_dict = token_dict["staking_contract"]
    del token_dict["staking_contract"]
    if staking_dict:  # staking_contract can be empty
        error, new_staking = create_item(models.Staking, staking_dict, current_user, db)
        if error:
            return error
        token_dict["staking_contract_id"] = new_staking["id"]

    presale_dict = token_dict["presale_contract"]
    del token_dict["presale_contract"]
    if presale_dict:  # presale_contract can be empty
        error, new_presale = create_item(models.Presale, presale_dict, current_user, db)
        if error:
            return error
        token_dict["presale_contract_id"] = new_presale["id"]

    error, new_token = create_item(models.Token, token_dict, current_user, db)
    if error:
        return error

    if not from_func:
        db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content=new_token)


@app.put("/tokens/{id}", tags=["token"])
def update_token(
    id: int,
    token_in: schemas.TokenUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, is_owner = check_authorization(id, current_user, db, models.Token, "cuser")
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    token_request = token_in.dict(exclude_unset=True)
    token_request["uuser"] = current_user.id

    # used setattr here for history(log) events to trigger.
    for k, v in token_request.items():
        setattr(token, k, v)
    db.commit()
    json_token = jsonable_encoder(token_request)

    return JSONResponse(status_code=status.HTTP_200_OK, content=json_token)


# @app.put("/tokens/{id}/approve")
# async def approve_token(
#     id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_active_superuser),
# ):
#     if (project := db.query(models.Project).get({"id": id})) is not None:
#         json_all_projects = jsonable_encoder(project)
#         return JSONResponse(status_code=status.HTTP_200_OK, content=json_all_projects)
#     raise HTTPException(status_code=404, detail="Project " + str(id) + " not found")


# SOCIALS PART------------------------------------------------
@app.get("/project/{id}/socials", tags=["social"])
def get_social(id: int, db: Session = Depends(get_db)):
    error, _, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    json_social = jsonable_encoder(project)["social"]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_social,
    )


@app.post("/project/{id}/socials", tags=["social"])
def create_social(
    id: int,
    socials_in: schemas.SocialSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, project_query, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    if project.social_id is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"project {id} already has socials. You can update them."
            },
        )

    social_dict = socials_in.dict()
    error, new_social = create_item(models.Social, social_dict, current_user, db)
    if error:
        return error

    project_request = {"social_id": new_social["id"]}
    try:
        project_query.update(project_request)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content=new_social)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@app.put("/project/{id}/socials", tags=["social"])
def update_social(
    id: int,
    socials_in: schemas.SocialSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, _, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    if project.social_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Project does not have socials. You can create it."},
        )

    error, is_owner = check_authorization(
        project.social_id, current_user, db, models.Social, "cuser"
    )
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    error, social_query, _ = get_db_object_by_id(models.Social, project.social_id, db)
    if error:
        return error

    social_request = socials_in.dict(exclude_unset=True)
    social_request["uuser"] = current_user.id
    social_query.update(social_request)
    db.commit()
    json_social = jsonable_encoder(social_request)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_social)


# ROUND PART-------------------------------------------------
@app.get("/project/{id}/round", tags=["round"])
def get_rounds(id: int, db: Session = Depends(get_db)):
    error, _, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    json_project = jsonable_encoder(project)
    round = "round_"
    json_round = {}
    for r in [
        "sale",
        "registration",
        "staking",
        "validation",
        "privatesale",
        "publicsale",
    ]:
        json_round[round + r] = json_project[round + r]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_round,
    )


@app.get("/project/{project_id}/round/{round_type}", tags=["round"])
def get_round(
    project_id: int, round_type: schemas.RoundType, db: Session = Depends(get_db)
):
    error, _, project = get_db_object_by_id(models.Project, project_id, db)
    if error:
        return error

    json_project = jsonable_encoder(project)
    if not json_project["round_" + round_type.value]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"{round_type.value} round does not exist for project {json_project['id']}"
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_project["round_" + round_type.value],
    )


@app.post("/project/{id}/round/{round_type}", tags=["round"])
def create_round(
    id: int,
    round_type: schemas.RoundType,
    round_in: schemas.RoundCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, project_query, project = get_db_object_by_id(models.Project, id, db)
    if error:
        return error

    json_project = jsonable_encoder(project)
    if json_project["round_" + round_type.value]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"{round_type.value} round already exist for project {json_project['id']}"
            },
        )

    round_dict = round_in.dict()
    round_dict["round_type"] = round_type.value
    error, new_round = create_item(models.Round, round_dict, current_user, db)
    if error:
        return error

    project_request = {"round_" + round_type.value + "_id": new_round["id"]}
    try:
        project_query.update(project_request)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content=new_round)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@app.put("/project/{project_id}/round/{round_type}", tags=["round"])
def update_round(
    project_id: int,
    round_type: schemas.RoundType,
    round_in: schemas.RoundUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, _, project = get_db_object_by_id(models.Project, project_id, db)
    if error:
        return error

    json_project = jsonable_encoder(project)
    if not json_project["round_" + round_type.value]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"{round_type.value} round does not exist for project {json_project['id']}"
            },
        )
    round_id = json_project["round_" + round_type.value]["id"]
    error, round_query, round = get_db_object_by_id(models.Round, round_id, db)
    if error:
        return error

    error, is_owner = check_authorization(
        round.id, current_user, db, models.Round, "cuser"
    )
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    round_request = round_in.dict(exclude_unset=True)
    round_request["uuser"] = current_user.id
    round_query.update(round_request)
    db.commit()
    json_round = jsonable_encoder(round_request)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_round)


# PRESALE PART-------------------------------------------------
@app.get("/token/{id}/presale", tags=["presale"])
def get_presale(id: int, db: Session = Depends(get_db)):
    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    token.presale_contract

    json_presale = jsonable_encoder(token)["presale_contract"]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_presale,
    )


@app.post("/token/{id}/presale", tags=["presale"])
def create_presale(
    id: int,
    presale_in: schemas.PresaleCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, token_query, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    if token.presale_contract_id is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"token {id} already has presale. You can update them."},
        )

    presale_dict = presale_in.dict()
    error, new_presale = create_item(models.Presale, presale_dict, current_user, db)
    if error:
        return error

    token_request = {"presale_contract_id": new_presale["id"]}
    try:
        token_query.update(token_request)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content=new_presale)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@app.put("/token/{id}/presale", tags=["presale"])
def update_presale(
    id: int,
    presale_in: schemas.PresaleUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    if token.presale_contract_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Token does not have presale. You can create it."},
        )

    error, is_owner = check_authorization(
        token.presale_contract_id, current_user, db, models.Presale, "cuser"
    )
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    error, presale_query, _ = get_db_object_by_id(
        models.Presale, token.presale_contract_id, db
    )
    if error:
        return error

    presale_request = presale_in.dict(exclude_unset=True)
    presale_request["uuser"] = current_user.id
    presale_query.update(presale_request)
    db.commit()
    json_presale = jsonable_encoder(presale_request)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_presale)


# STAKING PART-------------------------------------------------
@app.get("/token/{id}/stake", tags=["stake"])
def get_stake(id: int, db: Session = Depends(get_db)):
    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    token.staking_contract

    json_staking = jsonable_encoder(token)["staking_contract"]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_staking,
    )


@app.post("/token/{id}/stake", tags=["stake"])
def create_stake(
    id: int,
    stake_in: schemas.StakingCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, token_query, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    if token.staking_contract_id is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"token {id} already has staking. You can update them."},
        )

    stake_dict = stake_in.dict()
    error, new_stake = create_item(models.Staking, stake_dict, current_user, db)
    if error:
        return error

    token_request = {"staking_contract_id": new_stake["id"]}
    try:
        token_query.update(token_request)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content=new_stake)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@app.put("/token/{id}/stake", tags=["stake"])
def update_stake(
    id: int,
    stake_in: schemas.StakingUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    error, _, token = get_db_object_by_id(models.Token, id, db)
    if error:
        return error

    if token.staking_contract_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Token does not have stake. You can create it."},
        )

    error, is_owner = check_authorization(
        token.staking_contract_id, current_user, db, models.Staking, "cuser"
    )
    if error:
        return error
    if not is_owner:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "The user doesn't have enough privileges"},
        )

    error, stake_query, _ = get_db_object_by_id(
        models.Staking, token.staking_contract_id, db
    )
    if error:
        return error

    stake_request = stake_in.dict(exclude_unset=True)
    stake_request["uuser"] = current_user.id
    stake_query.update(stake_request)
    db.commit()
    json_stake = jsonable_encoder(stake_request)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_stake)


@app.get("/token/history", tags=["history"])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    try:
        history = db.query(models.Token_log).all()
    except sqlalchemy.exc.NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"history not found"},
        )
    json_history = jsonable_encoder(history)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_history,
    )


@app.post("/bsc", tags=["bsc"])
def get_bsc(
    bsc_in: schemas.BscSchema,
):
    api_address = os.getenv("bsc_api_url")
    params = bsc_in.params
    query_params = {
        "module": bsc_in.module,
        "action": bsc_in.action,
        "address": bsc_in.address,
        "apikey": os.getenv("bsc_api_key"),
    }
    if params is not None:
        query_params.update(params)
    resp = requests.get(
        url=api_address, headers={"User-Agent": "Mozilla/5.0"}, params=query_params
    )
    return resp.json()


def check_authorization(
    id: int, current_user: models.User, db: Session, cls, cls_params
):
    error, _, item = get_db_object_by_id(cls, id, db)
    if error:
        return error, False
    owner = jsonable_encoder(item)[cls_params]
    if owner == current_user.id or current_user.is_superuser:
        return None, True
    else:
        return None, False


@app.get("/contracts/abi", tags=["contracts"])
# def get_contracts_abi(current_user: models.User = Depends(get_current_active_user),):
def get_contracts_abi():

    dynamictoken_abi = json.load(open("./contracts/dynamictoken_abi", "r"))
    dynamictoken_presale_abi = json.load(
        open("./contracts/dynamictoken_presale_abi", "r")
    )
    unotoken_abi = json.load(open("./contracts/unotoken_abi", "r"))
    unotoken_presale_abi = json.load(open("./contracts/unotoken_presale_abi", "r"))
    rtrn_data = {
        "DUNOT_abi": dynamictoken_abi,
        "DUNOT_presale_abi": dynamictoken_presale_abi,
        "UNOT_abi": unotoken_abi,
        "UNOT_presale_abi": unotoken_presale_abi,
    }
    return (rtrn_data,)


@app.post("/transaction", tags=["contracts"])
async def post_transaction(
    transaction_in: schemas.TransactionCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    transaction_dict = transaction_in.dict()
    error, new_transaction = create_item(
        models.Transaction, transaction_dict, current_user, db
    )
    if error:
        return error
    if new_transaction["transaction_status"]:
        error, project_query, _ = get_db_object_by_id(
            models.Project, new_transaction["project_id"], db
        )
        if error:
            return error
        project = await get_project_by_id(new_transaction["project_id"], db)
        project = json.loads(project.body.decode())
        project["target_raised"] = (
            project["token"]["price_in_usd"] * project["token"]["distribution"]
        )
        project["total_tokens_sold"] = (
            project["total_tokens_sold"] + new_transaction["token_count"]
        )
        project["total_raised"] = (
            project["token"]["price_in_usd"] * project["total_tokens_sold"]
        )
        project["percent_raised"] = round(
            ((project["total_raised"] * 100) / project["target_raised"]), 2
        )
        project_query.update(
            {
                "target_raised": project["target_raised"],
                "total_tokens_sold": project["total_tokens_sold"],
                "total_raised": project["total_raised"],
                "percent_raised": project["percent_raised"],
            }
        )
        db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=project)

@app.post("/chain/{id}", tags=["contracts"])
def get_chain_info(
    id: int,
):
    try:
        for c_id in chains:
                u_id = c_id.get('chainId')
                if(id == u_id):
                    return JSONResponse(status_code=status.HTTP_200_OK, content=c_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )
