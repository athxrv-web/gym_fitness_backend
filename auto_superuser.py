import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
email = 'admin@gymfitness.com'
password = 'admin123456'

# Check karo agar user pehle se hai
if not User.objects.filter(email=email).exists():
    print(f"Creating superuser: {email}...")
    User.objects.create_superuser(email=email, password=password)
    print("✅ Superuser created successfully!")
else:
    print("ℹ️ Superuser already exists. Skipping.")