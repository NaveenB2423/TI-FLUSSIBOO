import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from domain.models import Image, Product

SRC_DIR = os.path.join(settings.BASE_DIR, "home", "static", "home", "images")

# Products in id order -> curated real photos (gender/type matched)
PRODUCT_IMAGES = [
    "gallery-03.jpg",   # Classic Cotton Tee (Men)
    "product-14.jpg",   # Graphic Print Tee (Men) - rose print
    "product-03.jpg",   # Formal Linen Shirt (Men) - gingham shirt
    "product-05.jpg",   # Floral Summer Dress (Women)
    "product-04.jpg",   # Elegant Maxi Dress (Women) - elegant coat
    "product-10.jpg",   # Casual Crop Top (Women)
]

# Banner records in id order -> curated real photos
BANNER_IMAGES = [
    "product-08.jpg", "product-14.jpg", "product-13.jpg",  # Printed T-Shirts (graphic/print tees)
    "product-07.jpg", "product-04.jpg", "product-16.jpg",  # For Women (New Arrivals / Dresses / Tops)
    "gallery-01.jpg", "product-11.jpg", "product-15.jpg",  # For Men (T-Shirts / Shirts / Essentials)
]


def _load(filename):
    path = os.path.join(SRC_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return ContentFile(fh.read())


class Command(BaseCommand):
    help = "Assign real template fashion photos to products and home banners."

    def handle(self, *args, **options):
        products = list(Product.objects.all().order_by("id"))
        for product, fname in zip(products, PRODUCT_IMAGES):
            content = _load(fname)
            if content is None:
                self.stdout.write(self.style.WARNING(f"missing source: {fname}"))
                continue
            if product.image:
                product.image.delete(save=False)
            product.image.save(f"product_{product.id}.jpg", content, save=True)
            self.stdout.write(self.style.SUCCESS(f"{product.name} <- {fname}"))

        banners = list(Image.objects.all().order_by("id"))
        for banner, fname in zip(banners, BANNER_IMAGES):
            content = _load(fname)
            if content is None:
                self.stdout.write(self.style.WARNING(f"missing source: {fname}"))
                continue
            if banner.image:
                banner.image.delete(save=False)
            banner.image.save(f"banner_{banner.id}.jpg", content, save=True)
            self.stdout.write(self.style.SUCCESS(f"{banner.name} <- {fname}"))

        self.stdout.write(self.style.SUCCESS("Real images assigned."))
