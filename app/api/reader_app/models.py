from tortoise import fields, Model

from app.api.access_app.models import ReaderGroups
from app.models import Users


class Readers(Users):
    nick_name = fields.CharField(max_length=32, description='昵称')
    age = fields.IntField(min_value=0, max_value=120, description='年龄')
    gender = fields.CharField(max_length=8, description='性别')
    password = fields.CharField(max_length=64, description='密码')
    avatar = fields.CharField(max_length=256, description='头像')
    group: fields.ManyToManyRelation[ReaderGroups]

    class Meta:
        table = 'reader'
