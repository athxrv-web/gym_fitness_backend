"""
Auto Create Superuser Script for Render Deployment
"""
import os
import django
from django.conf import settings

# 1. Django Environment Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    
    # 2. Get Credentials from Environment Variables (Render Dashboard se aayenge)
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
    last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

    if not email or not password:
        print("⚠️  Credentials not found in Environment Variables. Skipping Superuser creation.")
        return

    # 3. Check if User exists
    if User.objects.filter(email=email).exists():
        print(f"✅ User {email} already exists. Skipping.")
    else:
        # 4. Create New Superuser
        print(f"👤 Creating Superuser: {email}...")
        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='ADMIN'  # Tera Custom Role field
            )
            print("🎉 Superuser created successfully!")
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()