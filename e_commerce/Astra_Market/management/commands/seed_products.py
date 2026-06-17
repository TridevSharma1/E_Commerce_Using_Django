from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
import random
import io
from PIL import Image, ImageDraw, ImageFont
from Astra_Market.models import Category, Product

CATEGORY_NAMES = [
    'Electronics', 'Home & Kitchen', 'Fashion', 'Sports', 'Beauty',
    'Toys', 'Books', 'Automotive', 'Garden', 'Health'
]

SAMPLE_PRODUCTS = [
    'Wireless Headphones','Stainless Steel Kettle','Cotton T-Shirt','Yoga Mat','Skin Care Set',
    'Kids Building Blocks','Bestselling Novel','Car Phone Mount','Garden Hose','Vitamin C Tablets',
    'Bluetooth Speaker','Ceramic Dinner Set','Denim Jeans','Tennis Racket','Hair Conditioner',
    'Remote Control Car','Cookbook','LED Car Light','Garden Gloves','Protein Powder'
]

class Command(BaseCommand):
    help = 'Seed 10 categories and 20 products (idempotent)'

    def handle(self, *args, **options):
        # Create categories
        categories = []
        for name in CATEGORY_NAMES:
            slug = slugify(name)
            cat, created = Category.objects.get_or_create(name=name, slug=slug)
            categories.append(cat)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

        # Create products
        created_count = 0
        for i, title in enumerate(SAMPLE_PRODUCTS):
            # Ensure unique slug
            slug = slugify(title)
            if Product.objects.filter(slug=slug).exists():
                slug = f"{slug}-{i}"

            category = random.choice(categories)
            price = round(random.uniform(5.0, 299.99), 2)
            description = f"{title} is a high-quality product in the {category.name} category. Great value and reliable performance."

            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'category': category,
                    'description': description,
                    'price': price,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {title}'))
                # Generate a placeholder image for the product and attach it.
                image = Image.new('RGB', (800, 800), color=(random.randint(100, 220), random.randint(100, 220), random.randint(100, 220)))
                draw = ImageDraw.Draw(image)
                try:
                    font = ImageFont.truetype('arial.ttf', 40)
                except Exception:
                    font = ImageFont.load_default()
                text = title if len(title) <= 20 else title[:17] + '...'
                try:
                    w, h = font.getsize(text)
                except Exception:
                    bbox = font.getbbox(text)
                    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text(((800 - w) / 2, (800 - h) / 2), text, fill='white', font=font)
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                buffer.seek(0)
                product.image.save(f'{slug}.png', ContentFile(buffer.read()), save=True)

        self.stdout.write(self.style.SUCCESS(f'Seeding complete — {created_count} products created.'))
