import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trendylooms.settings')

application = get_wsgi_application()
app = application

# Auto-migrate on Vercel serverless cold start if using SQLite in /tmp
if (
    (os.environ.get('VERCEL') == '1' or bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME')))
    and not os.environ.get('DATABASE_URL')
):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Serverless migration notice: {e}", file=sys.stderr)

# Auto-seed default admin user if absent
try:
    from domain.models import User
    admin_user, created = User.objects.get_or_create(
        mobile_no='7845222924',
        defaults={
            'first_name': 'TI FLUSSIBOO',
            'last_name': 'Admin',
            'email': 'tiflussiboo@gmail.com',
            'role': 'Admin',
            'is_admin': True,
            'is_active': True,
        }
    )
    if created or not admin_user.is_admin:
        admin_user.set_password('Admin@12345')
        admin_user.is_admin = True
        admin_user.is_active = True
        admin_user.save()
# Auto-seed default demo customer if absent
try:
    from domain.models import User
    demo_user, c_created = User.objects.get_or_create(
        mobile_no='9876543210',
        defaults={
            'first_name': 'Demo',
            'last_name': 'Customer',
            'email': 'demo@tiflussiboo.com',
            'role': 'Customer',
            'is_admin': False,
            'is_active': True,
        }
    )
    if c_created or not demo_user.is_active:
        demo_user.set_password('Customer@123')
        demo_user.is_active = True
        demo_user.save()
        print("Initialized default demo customer: 9876543210", file=sys.stderr)
except Exception as e:
    print(f"Customer init notice: {e}", file=sys.stderr)



