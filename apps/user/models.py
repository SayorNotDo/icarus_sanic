from tortoise import Model, fields


class User(Model):
    uid = fields.IntField(pk=True)
    username = fields.CharField(50)
    chinese_name = fields.CharField(50)
    employee_id = fields.IntField()
    department = fields.CharField(255)
    position = fields.CharField(255)
    email = fields.TextField()
    phone = fields.CharField(255)
    join_date = fields.DateField()
    last_login_time = fields.DatetimeField()
    token = fields.TextField()
    access_token = fields.TextField()

    class Meta:
        table = "user"
        unique_together = ("uid", )
        indexes = ("uid", )

    def __str__(self):
        return f"{self.employee_id}-{self.username}-{self.chinese_name}-{self.position}"


def user_dict() -> dict:
    return {
        "uid": None,
        "username": "",
        "chinese_name": "",
        "employee_id": "",
        "department": "",
        "position": "",
        "email": "",
        "password": "",
        "phone": "",
        "join_date": "",
        "last_login_date": "",
        "token": "",
        "access_token": "",
    }
