from datetime import datetime, timedelta

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException
from tortoise.transactions import in_transaction

from src.app.api.book_app.models import Authors, Books, Category
from src.app.api.employee_app.data_pydantic import BooksItem, EmployeeItem
from src.app.api.employee_app.models import Employees
from src.app.core.config import settings
from src.app.utils.auth import create_access_token
from src.app.utils.totp_tools import create_totp_token

employee_routers = APIRouter()


@employee_routers.post('/login')
async def employee_login(item: EmployeeItem):
    """员工登录"""
    employee = await Employees.filter(phone=item.phone).first()
    if not employee or employee.is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='员工不存在',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    elif not employee.is_active:
        return {'msg': '员工未激活, 请前往激活'}

    # 验证
    if item.require_pass.upper() != create_totp_token(employee.secret_key):
        return {'msg': '「require_pass」无效或以失效'}

    now = datetime.today()
    employee.last_login = now
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = create_access_token(
        data={'ut': 'employee', 'uid': employee.id},
        expires_delta=access_token_expires,
    )

    return {'msg': '登录成功', 'access_token': access_token, 'token_type': 'bearer'}


@employee_routers.post('/books')
async def add_book(items: BooksItem):
    """入库新书"""
    results = []
    async with in_transaction():
        books_to_create, author_to_create = [], []
        for item in items.book_data:
            book = await Books.filter(book_name=item.book_name, bar_code=item.bar_code).first()
            if book:
                book.stock += item.stock
                if book.discount != item.discount:
                    book.price = item.price
                if book.discount != item.discount:
                    book.discount = item.discount
                await book.save()
                code = 2
                msg = f'书名「{book.book_name}」条码「{book.bar_code}」已更新'
            else:
                # 作者
                author_item = item.author
                # 获取已存在的作者
                author_exist = await Authors.filter(
                    name__in=[a_item.name for a_item in author_item]
                )
                exist_author_name = [ae.name for ae in author_exist]
                # 去除已存在的, 用不存在的数据创建 Authors 模型对象
                author_create = [
                    Authors(
                        name=a_item.name,
                        nationality=a_item.nationality,
                        gender=a_item.gender,
                    )
                    for a_item in author_item
                    if a_item.name not in exist_author_name
                ]
                author_to_create.extend(author_create)

                # 类别
                category_item = item.category
                # 检查是否存在
                category = await Category.filter(category_name=category_item.category_name).first()
                # 不存在责创建
                if not category:
                    # 检查父级是否存在
                    parent_category = await Category.filter(
                        category_name=category_item.parent
                    ).first()
                    # category_item.parent 不为空, 且不存在, 则需要创建
                    if category_item.parent and not parent_category:
                        parent_category = await Category.create(
                            category_name=category_item.parent, parent_category=None
                        )
                        await parent_category.save()
                    category = await Category.create(
                        category_name=category_item.category_name, parent_id=parent_category
                    )
                    await category.save()

                # 创建书籍
                book = Books(
                    book_name=item.book_name,
                    publisher=item.publisher,
                    price=item.price,
                    discount=item.discount,
                    category=category,
                    address=item.address,
                    bar_code=item.bar_code,
                    stock=item.stock,
                )

                books_to_create.append((
                    book,
                    author_exist,
                    author_create,
                ))

                code = 1
                msg = f'书名「{item.book_name}」条码「{item.bar_code}」已添加'
            results.append({
                'code': code,
                'msg': msg,
            })

        # 批量插入作者
        if author_to_create:
            await Authors.bulk_create(author_to_create)
        # 批量插入书籍
        if books_to_create:
            await Books.bulk_create([book for book, *_ in books_to_create])

            created_books = await Books.filter(
                book_name__in=[book.book_name for book, *_ in books_to_create]
            )
            book_map = {book.book_name: book for book in created_books}

            for book, author_exist, author_create in books_to_create:
                await book_map[book.book_name].author_id.add(*author_exist, *author_create)

    return {'data': results}
