from wagtail import hooks
from wagtail.admin.menu import MenuItem

@hooks.register('register_admin_menu_item')
def register_reviews_menu():
    return MenuItem(
        'Отзывы',
        '/django-admin/products/review/',
        icon_name='comment',
        order=400
    )

@hooks.register('register_admin_menu_item')
def register_review_images_menu():
    return MenuItem(
        'Фото отзывов',
        '/django-admin/products/reviewimage/',
        icon_name='image',
        order=401
    )