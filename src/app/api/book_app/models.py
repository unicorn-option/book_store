from tortoise import Model, fields

# 生成迁移文件后, 需要手动将 Category 的建表语句调整到 Books 的建表语句前面


class Books(Model):
    id = fields.IntField(pk=True)
    book_name = fields.CharField(max_length=32, description='书名')
    author_id = fields.ManyToManyField(
        model_name='models.Author',
        related_name='book',
        through='book_author',
    )
    publisher = fields.CharField(max_length=32, description='出版社')
    # max_digits: 有理数(十进制数)最大位数 decimal_places: 小数尾数
    price = fields.DecimalField(max_digits=10, decimal_places=2, description='价格')
    discount = fields.FloatField(description='折扣')
    category = fields.ForeignKeyField('models.Category', related_name='book', description='类别')
    address = fields.CharField(max_length=32, description='位置')
    bar_code = fields.CharField(max_length=32, description='条码')
    stock = fields.IntField(description='存量')
    available = fields.BooleanField(default=False, description='上架')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_time = fields.DatetimeField(auto_now=True, description='更新时间')
    is_delete = fields.BooleanField(default=False, description='是否已删除')

    class Meta:
        table = 'book'
        unique_together = (
            ('book_name', 'available')
        )


class Author(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, description='作者')
    nationality = fields.CharField(max_length=16, description='国籍')
    gender = fields.CharField(max_length=8, description='性别')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_time = fields.DatetimeField(auto_now=True, description='更新时间')
    is_delete = fields.BooleanField(default=False, description='是否已删除')

    class Meta:
        table = 'author'


class Category(Model):
    id = fields.IntField(pk=True)
    category_name = fields.CharField(max_length=16, description='')
    parent_id = fields.ForeignKeyField('models.Category', related_name='category', null=True)
