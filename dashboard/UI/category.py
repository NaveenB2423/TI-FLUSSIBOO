from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from domain.models import Color, MainMenus, Size, SubMenus
from .decorators import admin_required


# Main Menu
@admin_required
def create_main_menu(request):
    main_menus = MainMenus.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Menu name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'admin_page/category/menus/main_menus/add_main_menu.html', {'main_menus': main_menus})

            MainMenus.objects.create(name=name, priority=priority, status=1)
            messages.success(request, f'Main menu "{name}" created successfully.')
            return redirect('create_main_menu')

    return render(request, 'admin_page/category/menus/main_menus/add_main_menu.html', {'main_menus': main_menus})


@admin_required
def edit_main_menu(request, id):
    main_menus = MainMenus.objects.filter(status=1)
    selected_main_menu = get_object_or_404(MainMenus, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Menu name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'admin_page/category/menus/main_menus/edit_main_menu.html', {
                        'main_menus': main_menus,
                        'selected_main_menu': selected_main_menu,
                    })

            selected_main_menu.name = name
            selected_main_menu.priority = priority
            selected_main_menu.save()
            messages.success(request, f'Main menu "{name}" updated successfully.')
            return redirect('create_main_menu')

    return render(request, 'admin_page/category/menus/main_menus/edit_main_menu.html', {
        'main_menus': main_menus,
        'selected_main_menu': selected_main_menu,
    })


@admin_required
def delete_main_menu(request, id):
    selected_category = get_object_or_404(MainMenus, id=id)
    selected_category.status = 0
    selected_category.save()
    messages.success(request, f'Main menu "{selected_category.name}" removed.')
    return redirect('create_main_menu')


# Sub Menu
@admin_required
def create_sub_menu(request):
    sub_menus = SubMenus.objects.filter(status=1)
    main_menus = MainMenus.objects.filter(status=1)

    if request.method == 'POST':
        main_menu_id = request.POST.get('main_menu')
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, "Sub-menu name cannot be empty.")
        elif not main_menu_id:
            messages.error(request, "Please select a valid parent main menu.")
        else:
            try:
                main_menu = MainMenus.objects.get(id=main_menu_id, status=1)
                SubMenus.objects.create(main_menu=main_menu, name=name, status=1)
                messages.success(request, f'Sub-menu "{name}" created successfully.')
                return redirect('create_sub_menu')
            except MainMenus.DoesNotExist:
                messages.error(request, "Selected parent main menu not found.")

    return render(request, 'admin_page/category/menus/sub_menus/add_sub_menu.html', {
        'sub_menus': sub_menus,
        'main_menus': main_menus,
    })


@admin_required
def edit_sub_menu(request, id):
    sub_menus = SubMenus.objects.filter(status=1)
    main_menus = MainMenus.objects.filter(status=1)
    selected_sub_menu = get_object_or_404(SubMenus, id=id)

    if request.method == 'POST':
        main_menu_id = request.POST.get('main_menu')
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, "Sub-menu name cannot be empty.")
        elif not main_menu_id:
            messages.error(request, "Please select a valid parent main menu.")
        else:
            try:
                main_menu = MainMenus.objects.get(id=main_menu_id, status=1)
                selected_sub_menu.main_menu = main_menu
                selected_sub_menu.name = name
                selected_sub_menu.save()
                messages.success(request, f'Sub-menu "{name}" updated successfully.')
                return redirect('create_sub_menu')
            except MainMenus.DoesNotExist:
                messages.error(request, "Selected parent main menu not found.")

    return render(request, 'admin_page/category/menus/sub_menus/edit_sub_menu.html', {
        'sub_menus': sub_menus,
        'main_menus': main_menus,
        'selected_sub_menu': selected_sub_menu,
    })


# Colors
@admin_required
def add_color(request):
    colors = Color.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, "Color name cannot be empty.")
        else:
            Color.objects.create(name=name, status=1)
            messages.success(request, f'Color "{name}" added successfully.')
            return redirect('add_color')

    return render(request, 'admin_page/category/color/add_color.html', {'colors': colors})


@admin_required
def edit_color(request, id):
    colors = Color.objects.filter(status=1)
    selected_color = get_object_or_404(Color, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, "Color name cannot be empty.")
        else:
            selected_color.name = name
            selected_color.save()
            messages.success(request, f'Color "{name}" updated successfully.')
            return redirect('add_color')

    return render(request, 'admin_page/category/color/edit_color.html', {
        'colors': colors,
        'selected_color': selected_color,
    })


@admin_required
def delete_color(request, id):
    selected_color = get_object_or_404(Color, id=id)
    selected_color.status = 0
    selected_color.save()
    messages.success(request, f'Color "{selected_color.name}" removed.')
    return redirect('add_color')


# Sizes
@admin_required
def add_size(request):
    sizes = Size.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, "Size name cannot be empty.")
        else:
            Size.objects.create(name=name, status=1)
            messages.success(request, f'Size "{name}" added successfully.')
            return redirect('add_size')

    return render(request, 'admin_page/category/size/add_size.html', {'sizes': sizes})


@admin_required
def edit_size(request, id):
    sizes = Size.objects.filter(status=1)
    selected_size = get_object_or_404(Size, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, "Size name cannot be empty.")
        else:
            selected_size.name = name
            selected_size.save()
            messages.success(request, f'Size "{name}" updated successfully.')
            return redirect('add_size')

    return render(request, 'admin_page/category/size/add_size.html', {
        'sizes': sizes,
        'selected_size': selected_size,
    })


@admin_required
def delete_size(request, id):
    selected_size = get_object_or_404(Size, id=id)
    selected_size.status = 0
    selected_size.save()
    messages.success(request, f'Size "{selected_size.name}" removed.')
    return redirect('add_size')