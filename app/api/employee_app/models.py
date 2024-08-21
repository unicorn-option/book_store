from tortoise import fields, Model

from app.api.access_app.models import EmployeeGroups
from app.models import Users


class Departments(Model):
    id = fields.IntField(pk=True)
    dept_name = fields.CharField(max_length=32, description='部门名称')
    parent_dept = fields.ForeignKeyField(
        model_name='models.Departments',
        related_name='child_department',
        null=True,
        on_delete=fields.SET_NULL,
    )
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    is_delete = fields.BooleanField(default=False, description='是否已删除')

    class Meta:
        table = 'department'


class Employees(Users):
    gender = fields.CharField(max_length=8, description='性别')
    # # 使用用户保存的公钥加密, 服务器保存的私钥解密的方式认证
    # private_key = fields.CharField(max_length=2048, default='', description='公钥 key')
    # 使用 TOTP 方式认证
    secret_key = fields.CharField(max_length=128, default='', description='totp 密钥')
    department_id = fields.ForeignKeyField(
        model_name='models.Departments',
        related_name='employees',
        null=True,
        on_delete=fields.SET_NULL,
    )
    group: fields.ManyToManyRelation[EmployeeGroups]

    class Meta:
        table = 'employee'


class Managers(Model):
    id = fields.IntField(pk=True)
    dept_id = fields.ForeignKeyField(
        model_name='models.Departments',
        related_name='managers',
        null=True,
        on_delete=fields.SET_NULL,
    )
    employee_id = fields.ForeignKeyField(
        model_name='models.Employees',
        related_name='positions',
        null=True,
        on_delete=fields.SET_NULL,
    )
    title = fields.CharField(max_length=32, description='职位名称')
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    is_active = fields.BooleanField(default=False, description='是否已激活')
    is_delete = fields.BooleanField(default=False, description='是否已删除')
