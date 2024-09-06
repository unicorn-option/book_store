from src.app.api.book_app.data_pydantic import CategoryItem
from src.app.api.book_app.models import Category


async def create_category_object(
        item: CategoryItem,
        category_to_create: dict,
        parent_to_update: dict,
        category_names: list,
):
    names = [item.category_name]
    if item.parent:
        names.append(item.parent)
    categories = await Category.filter(category_name__in=names).all()
    category_ojb, parent_obj = None, None
    for category in categories:
        if category.category_name == item.category_name:
            category_ojb = category
        elif category.category_name == item.parent:
            parent_obj = category

    if not category_ojb and parent_obj:
        category_to_create[item.category_name] = Category(
            category_name=item.category_name,
            parent_id=parent_obj
        )
        category_names.append(item.category_name)
    elif category_ojb and not parent_obj:
        category_to_create[item.parent] = Category(category_name=item.parent)
        parent_to_update[category_ojb.category_name] = item.parent
        category_names.extend([category_ojb.category_name, item.parent])
    elif category_ojb and parent_obj:
        if category_ojb.parent_id != parent_obj:
            category_ojb.parent_id = parent_obj
            await category_ojb.save()
    elif not category_ojb and not item.parent:
        category_to_create[item.category_name] = Category(category_name=item.category_name)
        category_names.append(item.category_name)
    else:
        category_to_create[item.category_name] = Category(category_name=item.category_name)
        category_to_create[item.parent] = Category(category_name=item.parent)
        parent_to_update[item.category_name] = item.parent
        category_names.extend([item.category_name, item.parent])
