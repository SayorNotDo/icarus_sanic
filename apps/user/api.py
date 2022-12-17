import datetime
from json import dumps
from sanic import Blueprint
from sanic.response import json
from sanic_jwt import exceptions, protected, inject_user
from sanic_jwt.exceptions import Unauthorized
from apps.user.models import User
from static.ResponseBody import ResponseBody
from static.StatusCode import StatusCode
from exception.UserException import UserNotExist, MissParameters
from utils.logger import logger
from utils.DateEncoder import DateEncoder
from service.user_service import UserService

user_bp = Blueprint("user", url_prefix="/user")


@user_bp.route("/user_list", methods=["GET"])
async def user_list(request):
    users = await User.all()
    print("________________debug: ", users)
    response = ResponseBody(message="check",
                            status_code=StatusCode.MISSPARAMETERS.name)
    return json(response.__dict__)


@user_bp.route("/validate_password", methods=["POST"])
async def validate_password(request):
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        response = ResponseBody(message="username or password empty",
                                status_code=StatusCode.USERNAME_OR_PASSWORD_EMPTY.name)
        return json(response.__dict__)
    user = await User.filter(username=username, password=password).first()
    if not user:
        response = ResponseBody(message="user is not exist",
                                status_code=StatusCode.USER_NOT_EXIST.name)
        return json(response.__dict__)
    response = {
        "message": "password validate success",
        "status_code": "VALIDATE_SUCCESS",
        "code": 200
    }
    return json(response)


async def authenticate(request, *args, **kwargs):
    """ validate the user and password and authenticate """
    print("authenticate json_data: ", request.json)
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password")
    user = await User.filter(username=username, password=password).first()
    try:
        if user:
            user.last_login_time = datetime.datetime.now()
            await user.save()
            logger.info(f"User: {user.__dict__}")
            return user.__dict__
        else:
            raise exceptions.AuthenticationFailed(
                "User not found or password is incorrect")
    except UserNotExist:
        raise exceptions.AuthenticationFailed("User not exist")


async def retrieve_user(request, payload, *args, **kwargs):
    """ return user """
    print("_______________________debug")
    print(f"payload: {payload}")
    if payload:
        uid = payload.get("uid", None)
        if uid:
            user = User.filter(uid=uid).first()
            return json(user.__dict__)
        else:
            return None
    else:
        return None


@user_bp.route("/add_user", methods=["POST"])
# @inject_user()
# @protected()
async def add_user(request, user=None):
    """ add a user, need administrator identify """
    print(request.json)
    response = ResponseBody(
        message="check", status_code=200)
    return json(response.__dict__)


@user_bp.route("/get_all_user_information", methods=["GET"])
@inject_user()
@protected()
async def get_all_user_information(request, user):
    if not user.role:
        raise Unauthorized("You have no authorized to get user information")
    users = User.all()
    response = ResponseBody(
        message=users, status_code=StatusCode.PERMISSION_AVAILABLE.name)
    return json(response.__dict__)


@user_bp.route("/get_user_information", methods=["GET"])
@inject_user()
@protected()
async def get_user_information(request, user):
    if not request.json:
        raise MissParameters("no parameter send")
    uid = request.json.get("uid", None)
    username = request.json.get("username", None)
    if not user.role_id:
        raise Unauthorized("You have no authorized to get user information")
    if not username:
        raise MissParameters("username is empty")
    if not uid:
        raise MissParameters("uid is empty")
    user_info = User.filter(uid=uid, username=username).first()
    print("_____________debug: ", user_info.__dict__)
    if user_info:
        response = ResponseBody(
            message=user_info.__dict__, status_code=StatusCode.PERMISSION_AVAILABLE.name)
        return json(response.__dict__)
