from tortoise import fields

from src.app.api.access_app.models import ReaderGroups
from src.app.models import Users


class Readers(Users):
    nick_name = fields.CharField(max_length=32, description='昵称')
    age = fields.IntField(description='年龄')
    gender = fields.CharField(max_length=8, description='性别')
    password = fields.CharField(max_length=64, description='密码')
    avatar = fields.CharField(max_length=256, description='头像')
    group: fields.ManyToManyRelation[ReaderGroups]

    async def save(self, *args, **kwargs):
        if self.age < 0 or self.age > 120:
            raise ValueError("年龄必须在 0~120之间")
        await super(Readers, self).save(*args, **kwargs)

    class Meta:
        table = 'reader'
