from tortoise import Model, fields


class Users(Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=16, index=True, unique=True, null=False, description='')
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    last_login = fields.DatetimeField(null=True, description='最后登录时间')
    is_active = fields.BooleanField(default=False, description='是否已激活')
    is_delete = fields.BooleanField(default=False, description='是否已删除')

    class Meta:
        abstract = True
