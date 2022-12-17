from apps.task.api import task_bp
from apps.user.api import user_bp
from sanic.blueprints import Blueprint

api = Blueprint.group([user_bp], url_prefix="/api", version=1)

inner_api = Blueprint.group([task_bp], url_prefix="/inner", version=1)

