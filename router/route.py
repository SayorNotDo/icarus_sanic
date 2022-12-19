from apps.task.controller import task_bp
from apps.user.controller import user_bp
from sanic.blueprints import Blueprint

# api = Blueprint.group([user_bp], url_prefix="/api", version=1)

inner_api = Blueprint.group([task_bp, user_bp], url_prefix="/inner", version=1)

