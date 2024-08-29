from tortoise import Model, fields

# from app.api.employee_app.models import Employees
# from app.api.reader_app.models import Readers


class UserGroups(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, null=False, description='用户组名称')
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    is_active = fields.BooleanField(default=False, description='是否已激活')
    is_delete = fields.BooleanField(default=False, description='是否已删除')
    permission_id: fields.ManyToManyRelation['Permissions'] = fields.ManyToManyField(
        model_name='models.Permissions',
        related_name='user_group',
        through='user_group_permission_rel',
    )

    class Meta:
        table = 'user_group'


class Permissions(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, null=False, description='权限名称')
    api_path = fields.CharField(max_length=32, null=False, description='API 路径')
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    is_active = fields.BooleanField(default=False, description='是否已激活')
    is_delete = fields.BooleanField(default=False, description='是否已删除')
    user_group: fields.ManyToManyRelation['UserGroups']

    class Meta:
        table = 'permission'


class ReaderGroups(Model):
    id = fields.IntField(pk=True)
    parent_id = fields.ForeignKeyField(
        model_name='models.UserGroups',
        related_name='reader_group',
        null=True,
        on_delete=fields.SET_NULL,
    )
    reader_id: fields.ManyToManyRelation['Readers'] = fields.ManyToManyField(  # noqa: F821
        model_name='models.Readers',
        related_name='group',
        through='reader_reader_group_rel',
    )
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = 'reader_group'


class EmployeeGroups(Model):
    id = fields.IntField(pk=True)
    parent_id = fields.ForeignKeyField(
        model_name='models.UserGroups',
        related_name='employee_group',
        null=True,
        on_delete=fields.SET_NULL,
    )
    employee_id: fields.ManyToManyRelation['Employees'] = fields.ManyToManyField(  # noqa: F821
        model_name='models.Employees',
        related_name='group',
        through='employee_employee_group_rel',
    )
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = 'employee_group'
