import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

User = get_user_model()

# This is YOUR developer account
USERNAME = "developer"
PASSWORD = "devpassword123"  # You can change this later!
EMAIL = "dev@example.com"

if not User.objects.filter(username=USERNAME).exists():
    print(f"Creating superuser: {USERNAME}")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print("Developer account already exists.")