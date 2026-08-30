from django.core.management.base import BaseCommand
from domain.models import User


class Command(BaseCommand):
    help = 'Creates or updates the default admin user account'

    def add_arguments(self, parser):
        parser.add_argument('--mobile', type=str, default='7845222924', help='Admin Mobile Number')
        parser.add_argument('--password', type=str, default='Admin@12345', help='Admin Password')

    def handle(self, *args, **options):
        mobile = options['mobile']
        password = options['password']

        user, created = User.objects.get_or_create(
            mobile_no=mobile,
            defaults={
                'first_name': 'TI FLUSSIBOO',
                'last_name': 'Admin',
                'email': 'tiflussiboo@gmail.com',
                'role': 'Admin',
                'is_admin': True,
                'is_active': True,
            }
        )

        user.set_password(password)
        user.is_admin = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Admin user successfully created! Mobile: {mobile}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Admin user updated with new password! Mobile: {mobile}'))
