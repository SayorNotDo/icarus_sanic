from decorator.singleton import singleton
from apps.user.models import User


@singleton
class UserService:
    """ user @singleton to avoid create amount of same instance, improve the efficiency"""

    def __init__(self):
        self.User = User

    def get_all_user_information(self):
        """ query from db
        Args:
            user (User): User instance
        Returns:
            User: user information"""
        info = self.User.all()
        print("_____________debug: {}".format(info))
        users = []
        for row in info:
            users.append(row.__dict__)
        return users

