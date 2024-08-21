from tortoise import fields

from app.models import Users


class Administrator(Users):
    password = fields.CharField(max_length=64, description='密码')
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Administrator, cls).__new__(cls)
        return cls._instance

    class Meta:
        table = 'administrator'
