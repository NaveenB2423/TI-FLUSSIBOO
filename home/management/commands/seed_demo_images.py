import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from domain.models import Image, Product

# (top color, bottom color) gradients keyed loosely by product/category vibe
PALETTES = [
    ((124, 113, 255), (66, 56, 157)),
    ((255, 138, 101), (191, 73, 51)),
    ((38, 198, 218), (20, 110, 130)),
    ((236, 110, 173), (150, 45, 110)),
    ((129, 199, 132), (46, 110, 70)),
    ((255, 183, 77), (181, 110, 20)),
    ((96, 125, 200), (40, 55, 120)),
    ((171, 130, 220), (95, 60, 150)),
    ((255, 112, 112), (170, 50, 50)),
]


def _font(size):
    """Best-effort truetype font, falling back to PIL's default."""
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size, top, bottom):
    w, h = size
    base = PILImage.new("RGB", size, top)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base


def _centered(draw, text, font, box):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - tw) / 2 - bbox[0]
    y = box[1] + (box[3] - box[1] - th) / 2 - bbox[1]
    return x, y


def _fit_font(draw, text, start_size, max_width):
    """Shrink font until text fits within max_width."""
    size = start_size
    while size > 12:
        font = _font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 4
    return _font(size)


def make_placeholder(size, palette, title, subtitle=""):
    img = _gradient(size, *palette)
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = size

    # soft decorative circles
    draw.ellipse([w * 0.62, -h * 0.22, w * 1.15, h * 0.45],
                 fill=(255, 255, 255, 28))
    draw.ellipse([-w * 0.18, h * 0.62, w * 0.32, h * 1.18],
                 fill=(0, 0, 0, 30))

    title_font = _fit_font(draw, title, int(h * 0.11), w * 0.86)
    sub_font = _font(int(h * 0.05))

    tx, ty = _centered(draw, title, title_font, (0, h * 0.30, w, h * 0.55))
    draw.text((tx, ty), title, font=title_font, fill=(255, 255, 255))

    if subtitle:
        sx, sy = _centered(draw, subtitle, sub_font, (0, h * 0.55, w, h * 0.70))
        draw.text((sx, sy), subtitle, font=sub_font, fill=(255, 255, 255, 220))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Generate and assign demo placeholder images for products and banners."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate images even if one is already assigned.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        products = Product.objects.all().order_by("id")
        for idx, product in enumerate(products):
            if product.image and not force:
                self.stdout.write(f"skip product: {product.name} (has image)")
                continue
            palette = PALETTES[idx % len(PALETTES)]
            subtitle = product.main_menu.name
            if product.sub_menu:
                subtitle += f"  /  {product.sub_menu.name}"
            content = make_placeholder((900, 1100), palette, product.name, subtitle)
            if product.image:
                product.image.delete(save=False)
            product.image.save(f"product_{product.id}.jpg", content, save=True)
            self.stdout.write(self.style.SUCCESS(f"product image set: {product.name}"))

        banners = Image.objects.all().order_by("id")
        for idx, banner in enumerate(banners):
            if banner.image and not force:
                self.stdout.write(f"skip banner: {banner.name} (has image)")
                continue
            palette = PALETTES[(idx + 2) % len(PALETTES)]
            content = make_placeholder(
                (1000, 750), palette, banner.name or "Collection", banner.describe or ""
            )
            if banner.image:
                banner.image.delete(save=False)
            banner.image.save(f"banner_{banner.id}.jpg", content, save=True)
            self.stdout.write(self.style.SUCCESS(f"banner image set: {banner.name}"))

        self.stdout.write(self.style.SUCCESS("Demo images generated."))
