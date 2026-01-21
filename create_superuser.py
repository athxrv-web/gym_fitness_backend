import os
import django

# Django setup karo
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

# Check karo agar 'admin' pehle se hai ya nahi
if not User.objects.filter(username='admin').exists():
    # Agar nahi hai, toh bana do
    User.objects.create_superuser('admin', '', 'admin123')
    print("✅ Superuser 'admin' created successfully!")
else:
    print("ℹ️ Superuser 'admin' already exists.")