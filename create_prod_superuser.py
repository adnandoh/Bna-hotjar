import os
import django
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

def create_superuser():
    username = 'adnan'
    password = '9619'
    email = 'adnan@example.com'  # Default email

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created successfully!")
    else:
        print(f"⚠️ Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_superuser()
