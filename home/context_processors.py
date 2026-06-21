from domain.models import Cart, MainMenus


def insert_nav_bar_data(request):
    menus = MainMenus.objects.filter(status=1).order_by('priority')
    try:
        cart_counts = Cart.objects.filter(made_by=request.user).count()
    except Exception:
        cart_counts = 0
    return dict(menus=menus, cart_counts=cart_counts)
