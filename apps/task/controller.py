from sanic import Blueprint
from sanic.response import json
from static.ResponseBody import ResponseBody
from static.StatusCode import StatusCode

task_bp = Blueprint(name="task", url_prefix="/task")


@task_bp.route("/task_debug", methods=["POST"])
async def task_list(request):
    print("________________debug: ")
    response = ResponseBody(message="check",
                            status_code=StatusCode.MISSPARAMETERS.name)
    return json(response.__dict__)