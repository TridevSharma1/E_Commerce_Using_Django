from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Category, CustomUser, Product


class CategoryCreationTests(TestCase):
    def test_category_can_be_created_with_name_and_image(self):
        staff_user = CustomUser.objects.create_superuser(
            email='staff@example.com',
            full_name='Staff User',
            mobile='3333333333',
            password='StrongPass123',
        )
        image = BytesIO()
        from PIL import Image

        Image.new('RGB', (100, 100), color=(255, 0, 0)).save(image, format='PNG')
        image.seek(0)
        uploaded_image = SimpleUploadedFile(
            'category.png',
            image.getvalue(),
            content_type='image/png',
        )

        self.client.force_login(staff_user)
        response = self.client.post(reverse('category'), {
            'name': 'New Category',
            'image': uploaded_image,
        })

        self.assertEqual(response.status_code, 302)
        category = Category.objects.get(name='New Category')
        self.assertTrue(category.slug)
        self.assertTrue(category.image)


class PermissionTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='user@example.com',
            full_name='Normal User',
            mobile='1111111111',
            password='StrongPass123',
        )
        self.superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            mobile='2222222222',
            password='StrongPass123',
        )

    def test_regular_user_cannot_create_category(self):
        image = BytesIO()
        from PIL import Image

        Image.new('RGB', (100, 100), color=(255, 0, 0)).save(image, format='PNG')
        image.seek(0)
        uploaded_image = SimpleUploadedFile(
            'blocked-category.png',
            image.getvalue(),
            content_type='image/png',
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('category'), {
            'name': 'Blocked Category',
            'image': uploaded_image,
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(name='Blocked Category').exists())

    def test_superuser_can_create_product(self):
        category = Category.objects.create(name='Electronics', slug='electronics')
        self.client.force_login(self.superuser)

        response = self.client.post(reverse('products'), {
            'title': 'New Product',
            'description': 'Amazing new product',
            'price': '19.99',
            'category': category.id,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(title='New Product').exists())


class AccountCrudTests(TestCase):
    def test_user_can_register_and_delete_account(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'mobile': '9876543210',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
            'accept_terms': 'on',
        })

        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(email='jane@example.com')
        self.assertEqual(user.mobile, '9876543210')

        self.client.force_login(user)
        delete_response = self.client.post(reverse('delete_account'))

        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(CustomUser.objects.filter(pk=user.pk).exists())
