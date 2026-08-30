from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from domain.models import Category, Color, Size
from .decorators import admin_required


@admin_required
def category(request):
    categories = Category.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Category name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/category.html', {'categories': categories})

            Category.objects.create(name=name, priority=priority, status=1)
            messages.success(request, f'Category "{name}" created successfully.')
            return redirect('category')

    return render(request, 'specification/category.html', {'categories': categories})


@admin_required
def edit_category(request, id):
    categories = Category.objects.filter(status=1)
    selected_category = get_object_or_404(Category, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Category name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/edit_category.html', {
                        'categories': categories,
                        'selected_category': selected_category,
                    })

            selected_category.name = name
            selected_category.priority = priority
            selected_category.save()
            messages.success(request, f'Category "{name}" updated successfully.')
            return redirect('category')

    return render(request, 'specification/edit_category.html', {
        'categories': categories,
        'selected_category': selected_category,
    })


@admin_required
def delete_category(request, id):
    selected_category = get_object_or_404(Category, id=id)
    selected_category.status = 0
    selected_category.save()
    messages.success(request, f'Category "{selected_category.name}" removed.')
    return redirect('category')


@admin_required
def color(request):
    colors = Color.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Color name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/color.html', {'colors': colors})

            Color.objects.create(name=name, priority=priority, status=1)
            messages.success(request, f'Color "{name}" created successfully.')
            return redirect('color')

    return render(request, 'specification/color.html', {'colors': colors})


@admin_required
def edit_color(request, id):
    colors = Color.objects.filter(status=1)
    selected_color = get_object_or_404(Color, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Color name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/edit_color.html', {
                        'colors': colors,
                        'selected_color': selected_color,
                    })

            selected_color.name = name
            selected_color.priority = priority
            selected_color.save()
            messages.success(request, f'Color "{name}" updated successfully.')
            return redirect('color')

    return render(request, 'specification/edit_color.html', {
        'colors': colors,
        'selected_color': selected_color,
    })


@admin_required
def delete_color(request, id):
    selected_color = get_object_or_404(Color, id=id)
    selected_color.status = 0
    selected_color.save()
    messages.success(request, f'Color "{selected_color.name}" removed.')
    return redirect('color')


@admin_required
def size(request):
    sizes = Size.objects.filter(status=1)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Size name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/size.html', {'sizes': sizes})

            Size.objects.create(name=name, priority=priority, status=1)
            messages.success(request, f'Size "{name}" created successfully.')
            return redirect('size')

    return render(request, 'specification/size.html', {'sizes': sizes})


@admin_required
def edit_size(request, id):
    sizes = Size.objects.filter(status=1)
    selected_size = get_object_or_404(Size, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_priority = request.POST.get('priority_no', '').strip()

        if not name:
            messages.error(request, "Size name cannot be empty.")
        else:
            priority = None
            if raw_priority:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    messages.error(request, "Priority must be a valid integer number.")
                    return render(request, 'specification/edit_size.html', {
                        'sizes': sizes,
                        'selected_size': selected_size,
                    })

            selected_size.name = name
            selected_size.priority = priority
            selected_size.save()
            messages.success(request, f'Size "{name}" updated successfully.')
            return redirect('size')

    return render(request, 'specification/edit_size.html', {
        'sizes': sizes,
        'selected_size': selected_size,
    })


@admin_required
def delete_size(request, id):
    selected_size = get_object_or_404(Size, id=id)
    selected_size.status = 0
    selected_size.save()
    messages.success(request, f'Size "{selected_size.name}" removed.')
    return redirect('size')