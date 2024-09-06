from datetime import datetime, timedelta

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException
from tortoise.transactions import in_transaction

from src.app.api.book_app.book_tools import create_category_object
from src.app.api.book_app.models import (
    Authors,
    Books,
    Category,
)
from src.app.api.employee_app.data_pydantic import (
    AuthorsItem,
    BooksItem,
    CategoriesItem,
    EmployeeItem,
)
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
        category_to_create, parent_category_to_update, book_category_dict = {}, {}, {}
        category_names = []
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
                await create_category_object(
                    item.category,
                    category_to_create,
                    parent_category_to_update,
                    category_names,
                )
                book_category_dict[item.book_name] = item.category.category_name
                # category_item = item.category
                # # 检查是否存在
                # category = await Category.filter(category_name=category_item.category_name).first()
                # # 不存在责创建
                # if not category:
                #     # 检查父级是否存在
                #     parent_category = await Category.filter(
                #         category_name=category_item.parent
                #     ).first()
                #     # category_item.parent 不为空, 且不存在, 则需要创建
                #     if category_item.parent and not parent_category:
                #         parent_category = await Category.create(
                #             category_name=category_item.parent, parent_category=None
                #         )
                #         await parent_category.save()
                #     category = await Category.create(
                #         category_name=category_item.category_name, parent_id=parent_category
                #     )
                #     await category.save()

                # 创建书籍
                book = Books(
                    book_name=item.book_name,
                    publisher=item.publisher,
                    price=item.price,
                    discount=item.discount,
                    # category=category,
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

        category_name_map = {}
        # 批量创建图书类别
        if category_to_create:
            await Category.bulk_create(list(category_to_create.values()))
            created_categories = await Category.filter(category_name__in=category_names)

            category_name_map = {category.category_name: category for category in created_categories}

            for category_name, parent_name in parent_category_to_update.items():
                category_name_map[category_name].parent_id = category_name_map[parent_name]
                await category_name_map[category_name].save()

        # 批量插入书籍
        if books_to_create:
            await Books.bulk_create([book for book, *_ in books_to_create])

            created_books = await Books.filter(
                book_name__in=[book.book_name for book, *_ in books_to_create]
            )
            book_map = {book.book_name: book for book in created_books}

            for book, author_exist, author_create in books_to_create:
                # 关联作者和图书类别时关于异步 await 的问题
                # /docs/images/asynchronous_await_when_associating_authors_and_book_categories.png
                book_map[book.book_name].author_id.add(*author_exist, *author_create)
                book_map[book.book_name].category = category_name_map.get(book_category_dict[book.book_name], None)
                await book_map[book.book_name].save()

    return {'data': results}


@employee_routers.post('/authors')
async def add_author(items: AuthorsItem):
    results = []
    async with in_transaction():
        author_to_create = []
        for item in items.author_data:
            author = await Authors.filter(name=item.name).first()
            if author:
                author.nationality = item.nationality
                await author.save()

                code = 2
                msg = f'作者「{author.name}」已更新'
            else:
                author_to_create.append(Authors(
                    name=item.name,
                    nationality=item.nationality,
                    gender=item.gender,
                ))

                code = 1
                msg = f'作者「{item.name}」已添加'

            results.append({
                'code': code,
                'msg': msg,
            })

        # 批量创建作者
        if author_to_create:
            await Authors.bulk_create(author_to_create)

    return {'data': results}


@employee_routers.post('/categories')
async def add_category(items: CategoriesItem):
    results = []
    async with in_transaction():
        category_to_create = {}
        parent_to_update = {}
        category_names = []
        for item in items.category_data:
            await create_category_object(item, category_to_create, parent_to_update, category_names)
            # names = [item.category_name]
            # if item.parent:
            #     names.append(item.parent)
            # categories = await Category.filter(category_name__in=names).all()
            # category_ojb, parent_obj = None, None
            # for category in categories:
            #     if category.category_name == item.category_name:
            #         category_ojb = category
            #     elif category.category_name == item.parent:
            #         parent_obj = category
            #
            # if not category_ojb and parent_obj:
            #     category_to_create.append(
            #         Category(
            #             category_name=item.category_name,
            #             parent_id=parent_obj
            #         )
            #     )
            #     category_names.append(item.category_name)
            # elif category_ojb and not parent_obj:
            #     category_to_create.append(
            #         Category(
            #             category_name=item.parent
            #         )
            #     )
            #     parent_to_update[category_ojb.category_name] = item.parent
            #     category_names.extend([category_ojb.category_name, item.parent])
            # elif category_ojb and parent_obj:
            #     if category_ojb.parent_id != parent_obj:
            #         category_ojb.parent_id = parent_obj
            #         await category_ojb.save()
            # elif not category_ojb and not item.parent:
            #     category_to_create.append(Category(category_name=item.category_name))
            #     category_names.append(item.category_name)
            # else:
            #     category_to_create.append(Category(category_name=item.category_name))
            #     category_to_create.append(Category(category_name=item.parent))
            #     parent_to_update[item.category_name] = item.parent
            #     category_names.extend([item.category_name, item.parent])

            results.append({
                'code': 1,
                'msg': f'「{item.category_name}」添加成功'
            })

        if category_to_create:
            await Category.bulk_create(list(category_to_create.values()))

            created_categories = await Category.filter(category_name__in=category_names)

            category_name_map = {category.category_name: category for category in created_categories}

            for category_name, parent_name in parent_to_update.items():
                category_name_map[category_name].parent_id = category_name_map[parent_name]
                await category_name_map[category_name].save()

    return {'data': results}
