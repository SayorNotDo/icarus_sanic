from tortoise import Model, fields
import datetime

class User(Model):
    uid = fields.IntField(pk=True)
    username = fields.CharField(50)
    chinese_name = fields.CharField(50)
    employee_id = fields.CharField(50)
    department = fields.CharField(255)
    position = fields.CharField(255)
    email = fields.TextField()
    phone = fields.CharField(255)
    join_date = fields.DateField()
    last_login_time = fields.DatetimeField()
    authorize_token = fields.TextField()

    class Meta:
        table = "user"
        unique_together = ("uid", )
        indexes = ("uid", )

    def __str__(self):
        return f"{self.employee_id}-{self.username}-{self.chinese_name}-{self.position}"


def user_dict(json_resp) -> dict:
    return {
        "uid": json_resp["Uid"],
        "username": json_resp["Username"],
        "chinese_name": json_resp["ChineseName"],
        "employee_id": json_resp["EmployeeId"],
        "department": json_resp["Department"],
        "position": json_resp["Position"],
        "email": json_resp["Email"],
        "phone": json_resp["Phone"],
        "join_date": json_resp["JoinDate"],
        "last_login_time": datetime.datetime.now(),
    }
