from sanic import Sanic
from sanic.exceptions import RequestTimeout, NotFound
from sanic.response import json
from sanic_jwt import initialize
from sanic_openapi import swagger_blueprint
from tortoise.contrib.sanic import register_tortoise

from apps.user.api import authenticate, retrieve_user
from apps.user.api import user_bp
from config.BaseConfig import BaseConfig
from config.Config import Config
from exception.UserException import UserAddException, MissParameters, UserDeleteException
from static.StatusCode import StatusCode

app = Sanic(__name__)
app.blueprint(swagger_blueprint)
app.static("/v1/data", "../../data")


@app.exception(RequestTimeout)
async def timeout(request, exception):
    response = {
        "reasons": ["Request Timeout"],
        "exception": StatusCode.REQUEST_TIMEOUT.name
    }
    return json(response, 408)


@app.exception(NotFound)
async def notfound(request, exception):
    response = {
        "reasons": [f"Requested URL {request.url} not found"],
        "exception": StatusCode.NOT_FOUND.name
    }
    return json(response, 404)


@app.exception(MissParameters)
async def miss_parameters(request, exception):
    response = {
        "reasons": [str(exception)],
        "exception": StatusCode.MISSPARAMETERS.name
    }
    return json(response, 401)


@app.exception(UserAddException)
async def add_user_exception_handle(request, exception):
    response = {
        "reasons": [str(exception)],
        "exception": StatusCode.ADD_USER_FAILED.name
    }
    return json(response, 401)


@app.exception(UserDeleteException)
async def delete_user_exception_handle(request, exception):
    response = {
        "reasons": [str(exception)],
        "exception": StatusCode.DELETE_USER_FAILED.name
    }
    return json(response, 401)


app.config.update_config(BaseConfig)
register_tortoise(
    app,
    config=app.config["DB_CONFIG"],
    generate_schemas=True
)

initialize(app,
           authenticate=authenticate,
           retrieve_user=retrieve_user,
           url_prefix="v1/api/auth")

app.blueprint(user_bp)
if __name__ == '__main__':
    port = int(Config.get_instance().get('http.port', 80))
    app.run(host="0.0.0.0", port=port)
