from django.urls import path
from . import specification
from . import product
from . import views 
from . import category
from . import customer

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard),
    path('create-main-menu/', category.create_main_menu, name='create_main_menu'),
    path('create-main-menu', category.create_main_menu),
    path('edit-main-menu/<int:id>/', category.edit_main_menu, name='edit_main_menu'),
    path('delete-main-menu/<int:id>/', category.delete_main_menu, name='delete_main_menu'),

    path('create-sub-menu/', category.create_sub_menu, name='create_sub_menu'),
    path('create-sub-menu', category.create_sub_menu),
    path('edit-sub-menu/<int:id>/', category.edit_sub_menu, name='edit_sub_menu'),
    path('add-color/', category.add_color, name='add_color'),
    path('add-color', category.add_color),
    path('edit-color/<int:id>/', category.edit_color, name='edit_color'),
    path('delete-color/<int:id>/', category.delete_color, name='delete_color'),
    path('add-size/', category.add_size, name='add_size'),
    path('add-size', category.add_size),
    path('edit-size/<int:id>/', category.edit_size, name='edit_size'),
    path('delete-size/<int:id>/', category.delete_size, name='delete_size'),

    # Customer
    path('addcustomer/', customer.add_customer, name='addcustomer'),
    path('addcustomer', customer.add_customer),
    path('listcustomer/', customer.view_customer, name='listcustomer'),
    path('listcustomer', customer.view_customer),
    path('view_design/', customer.view_design, name="view_design"),
    path('view_design', customer.view_design),

    path('category/', specification.category, name='category'),
    path('category', specification.category),
    path('edit-category/<int:id>/', specification.edit_category, name='edit_category'),
    path('delete-category/<int:id>/', specification.delete_category, name='delete_category'),
    
    path('get-sub-menus/', product.get_sub_menus, name='get_sub_menus'),
    path('get-sub-menus', product.get_sub_menus),
    path('add-product/', product.add_product, name='add_product'),
    path('add-product', product.add_product),
    path('list-products/', product.list_product, name='list_product'),
    path('list-products', product.list_product),
    path('edit-product/<int:id>/', product.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', product.delete_product, name='delete_product'),
    path('update-home-item/', product.update_home_item, name="update_home_item"),
    path('update-home-item', product.update_home_item),
    path('ecommerce/', product.ecommerce, name='ecommerce'),
    path('ecommerce', product.ecommerce),

    # Images
    path('image/', views.image, name='image'),
    path('image', views.image),
    path('get_image/', views.get_image, name='get_image'),
    path('get_image', views.get_image),
    path('delete-image/<int:id>/', views.delete_image, name='delete_image'),
]