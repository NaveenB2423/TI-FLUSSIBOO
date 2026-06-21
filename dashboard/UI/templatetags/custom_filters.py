from django import template
from domain.models import ProductVariant

register = template.Library()

@register.filter(name='distinct_sizes')
def distinct_sizes(product_variants):
    size_set = set()
    distinct_sizes = []

    for variant in product_variants:
        if variant.size.name not in size_set and variant.status == 1:
            size_set.add(variant.size.name)
            distinct_sizes.append(variant.size.name)
    return distinct_sizes


@register.filter
def distinct_colors(product_variants):
    color_set = set()
    distinct_colors = []
 
    

    for variant in product_variants:
        if variant.color.name not in color_set and variant.status == 1:
            color_set.add(variant.color.name)
            distinct_colors.append(variant.color.name)
    return distinct_colors


#not used
@register.simple_tag
def check_colors(product, color ):   
    variant = ProductVariant.objects.filter(product=product, color=color, status= 1).exists()

    if variant :
        return True
    else:
        return False
    

@register.simple_tag(name='check_sizes')
def check_sizes(product, size ):   
    variant = ProductVariant.objects.filter(product=product, size=size, status= 1).exists()
    
    if variant :
        return True
    else:
        return False
    
