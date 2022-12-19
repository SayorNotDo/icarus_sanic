from repository.repo import BaseRepository
from .models import User


class UserRepository(BaseRepository):
    MODEL_CLASS = User

    def __init__(self):
        super(UserRepository, self).__init__()
