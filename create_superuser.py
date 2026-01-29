import os
import django
from django.conf import settings

# 1. Django Environment Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    
    # 2. Ye code Render ki Settings se password uthayega
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
    last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

    # Agar Render pe settings nahi mili, toh ruk jao
    if not email or not password:
        print("⚠️ Credentials nahi mile Environment Variables mein. Skip kar raha hoon.")
        return

    # 3. Check karo agar user pehle se hai
    if User.objects.filter(email=email).exists():
        print(f"✅ User {email} pehle se maujood hai. Kuch karne ki zaroorat nahi.")
    else:
        # 4. Naya Superuser banao
        print(f"👤 Creating Superuser: {email}...")
        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='ADMIN'  # Tera Custom Role field
            )
            print("🎉 Superuser ban gaya successfully!")
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()