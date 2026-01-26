#!/usr/bin/env python
"""
Create superuser for Django admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fitness.models import User

def create_superuser():
    """Create superuser if it doesn't exist"""
    
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@gymfitness.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123456')
    
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        print(f'✅ Superuser created: {email}')
    else:
        print(f'ℹ️  Superuser already exists: {email}')

if __name__ == '__main__':
    create_superuser()