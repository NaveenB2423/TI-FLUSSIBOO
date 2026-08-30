from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_default_users(apps, schema_editor):
    User = apps.get_model('domain', 'User')

    # 1. Admin User
    admin_user, _ = User.objects.get_or_create(
        mobile_no='7845222924',
        defaults={
            'first_name': 'TI FLUSSIBOO',
            'last_name': 'Admin',
            'email': 'tiflussiboo@gmail.com',
            'role': 'Admin',
            'is_admin': True,
            'is_active': True,
            'is_password_set': True,
        }
    )
    admin_user.password = make_password('Admin@12345')
    admin_user.is_admin = True
    admin_user.is_active = True
    admin_user.save()

    # 2. Customer Demo User
    demo_user, _ = User.objects.get_or_create(
        mobile_no='9876543210',
        defaults={
            'first_name': 'Demo',
            'last_name': 'Customer',
            'email': 'demo@tiflussiboo.com',
            'role': 'Customer',
            'is_admin': False,
            'is_active': True,
            'is_password_set': True,
        }
    )
    demo_user.password = make_password('Customer@123')
    demo_user.is_admin = False
    demo_user.is_active = True
    demo_user.save()


def remove_default_users(apps, schema_editor):
    User = apps.get_model('domain', 'User')
    User.objects.filter(mobile_no__in=['7845222924', '9876543210']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_users, remove_default_users),
    ]
