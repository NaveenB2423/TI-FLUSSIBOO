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

