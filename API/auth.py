from datetime import datetime, timedelta
from typing import Any, Union
from sqlalchemy import null
from database import API_CLIENT, DB_NAME
import models, schemas
import secrets
import sqlalchemy.exc
from jose import jwt
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from typing import Any, Optional, Union, List
from models import User
from pydantic import ValidationError
from app import get_db, app, limiter
from reset_password import *
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
import random
from fastapi import Form
from starlette.requests import Request
import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = os.getenv("algorithm")
SECRET_KEY: str = secrets.token_urlsafe(32)

# 60 minutes * 24 hours * 8 days = 8 days
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("access_token_expire_minutes"))
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/login")
USEREMAIL = None


def get(db: Session, id: Any):
    return db.query(models.User).filter(models.User.id == id).first()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


async def get_current_user_email():
    return USEREMAIL


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    activision_status = is_active(current_user)
    if activision_status != "True":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_by_email(db: Session, *, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create(db: Session, *, obj_in: schemas.UserCreate, activation_code) -> User:
    # password_reset_token = generate_password_reset_token(email=obj_in.email)
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=activation_code,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    # send_new_account_email(
    #     email_to=obj_in.email,
    #     username=obj_in.email,
    #     token=password_reset_token,
    #     activation_code=activation_code,
    # )
    return db_obj


def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> str:
    return user.is_active


def is_superuser(user: User) -> bool:
    return user.is_superuser


@app.post("/login", response_model=schemas.Token, tags=["auth"])
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # TODO: aktif olmadan giriş yapabilecek mi?
    elif not is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    global USEREMAIL
    USEREMAIL = user.email
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": user.id,
            "full_name": user.full_name,
            "username": form_data.username,
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "is_active": user.is_active,
            "kyc_status": user.kyc_status,
            "kyc_reason": user.kyc_reason,
            "is_superuser": user.is_superuser,
        },
    )


@app.get("/users", response_model=List[schemas.User], tags=["user"])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve users.
    """
    users = get_multi(db, skip=skip, limit=limit)
    json_project = jsonable_encoder(users)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_project)


def activation_code():
    code = random.randint(100000, 999999)
    return code


@app.post("/signup", response_model=schemas.UserCreate, tags=["auth"])
def signup(
    *,
    db: Session = Depends(get_db),
    username: str = Form(),
    password: str = Form(),
    email: str = Form(),
) -> Any:
    """
    Create new user.
    """
    user_in = schemas.UserCreate
    user_in.full_name = username
    user_in.password = password
    user_in.email = email
    user = get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    try:
        if "Test" not in DB_NAME:
            simple_public_object_input = SimplePublicObjectInput(
                properties={"firstname": user_in.full_name, "email": user_in.email}
            )
            api_response = API_CLIENT.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )

        code = str(activation_code())
        user = create(db, obj_in=user_in, activation_code=code)
        json_project = jsonable_encoder(user)
        activation_token = generate_password_reset_token(email=user_in.email)
        if user_in.email:
            send_new_account_email(
                email_to=user_in.email,
                username=user_in.email,
                token=activation_token,
                activation_code=code,
            )
        json_project["activation_token"] = activation_token
        return JSONResponse(status_code=status.HTTP_200_OK, content=json_project)
    except ApiException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"Error: ": str(e)}
        )


@app.post("/password-recovery", response_model=schemas.PassToken, tags=["auth"])
def recover_password(db: Session = Depends(get_db), email: str = Form()) -> Any:
    """
    Password Recovery
    """
    user = get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(email_to=email, email=email, token=password_reset_token)
    return {"token": password_reset_token}


@app.post("/reset-password", response_model=schemas.Msg, tags=["auth"])
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}


def send_new_account_email(
    email_to: str, username: str, activation_code: str, token: str
) -> None:
    project_name = PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = f"{SERVER_HOST}/activate_user?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "username": username,
            "email": email_to,
            "activation_code": activation_code,
            "link": link,
        },
    )


@app.post("/activate", tags=["auth"])
def activate_user(
    token: str = Body(...),
    activation_code: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    activate user
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    if user.is_active == activation_code:
        user.is_active = "True"
        db.add(user)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "User Activated Successfully"})
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"msg": "Activation Code Is Not True"})


@app.put("/user/{id}/kyc", response_model=schemas.UserKYCUpdate, tags=["user"])
def user_kyc(
    id: int,
    kyc: schemas.UserKYCUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    hubspot_key = os.getenv("hubspot_api_key")
    reason = kyc.kyc_reason
    try:
        assert db.query(models.User).filter(models.User.id == id).one()
    except sqlalchemy.exc.NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"User {id} not found"},
        )
    if "Test" not in DB_NAME:
        url = (
            "https://api.hubapi.com/contacts/v1/contact/email/"
            + str(current_user.email)
            + "/profile?hapikey="
            + str(hubspot_key)
        )

        try:
            r = requests.get(url=url)
            contact_id = r.json()["vid"]
        except:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"error": "user not found"},
            )
        properties = {
            "hs_content_membership_status": "active",
            "hs_content_membership_notes": str(reason),
        }
        simple_public_object_input = SimplePublicObjectInput(properties=properties)
        try:
            api_response = API_CLIENT.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=simple_public_object_input,
            )
        except ApiException as e:
            print("Exception when calling basic_api->update: %s\n" % e)

    user = db.query(models.User).filter(models.User.id == id)
    user_request = kyc.dict(exclude_unset=True)
    user.update(user_request)
    db.commit()
    json_new_token = jsonable_encoder(user_request)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_new_token)


@app.post("/user/activation-email", tags=["user"])
@limiter.limit("1/minute")
def send_activation_email(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    code = str(activation_code())
    user_query = db.query(models.User).filter(models.User.email == current_user.email)
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if user.is_active != "True":
        activation_token = generate_password_reset_token(email=current_user.email)
        user_query.update({"is_active": code})
        db.commit()
        send_new_account_email(
            email_to=current_user.email,
            username=current_user.email,
            token=activation_token,
            activation_code=code,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"success": "activation email sent"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": "User already activated"},
        )


@app.get("/user/profile", tags=["user"])
def get_user_profile(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):

    try:
        user = (
            db.query(models.User)
            .filter(models.User.id == current_user.id)
            .with_entities(
                User.id,
                User.full_name,
                User.email,
                User.is_active,
                User.kyc_status,
                User.kyc_reason,
                User.is_superuser,
            )
            .one()
        )
    except sqlalchemy.exc.NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"User {id} not found"},
        )
    json_user = jsonable_encoder(user)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_user)


@app.get("/user/check_token", tags=["user"])
def check_user_token(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):

    return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "token active"})
