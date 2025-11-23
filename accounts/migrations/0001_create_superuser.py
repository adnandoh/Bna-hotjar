from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    username = 'adnan'
    password = '112233'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create(
            username=username,
            password=make_password(password),
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        print(f"Superuser '{username}' created.")
    else:
        print(f"Superuser '{username}' already exists.")

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
