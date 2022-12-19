from sanic import Sanic
from sanic.exceptions import RequestTimeout, NotFound
from sanic.response import json
from sanic_openapi import swagger_blueprint
from tortoise.contrib.sanic import register_tortoise
from router.route import inner_api
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


register_tortoise(app,
                  db_url="sqlite://db.sqlite3",
                  modules={"models": ["apps.user.models"]},
                  generate_schemas=True)

app.blueprint([
    inner_api,
])

if __name__ == '__main__':
    port = int(Config.get_instance().get('http.port', 80))
    app.run(host="0.0.0.0", port=port)
