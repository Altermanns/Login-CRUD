@echo off
echo 🚀 Starting Django application with SQLite...

echo 📋 Applying database migrations...
python manage.py migrate --noinput

echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo 👥 Creating default users...
python manage.py shell -c "
from django.contrib.auth.models import User
from Texcore.models import Profile
import os

admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@textilapp.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

try:
    if not User.objects.filter(username=admin_username).exists():
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='Sistema'
        )
        profile, created = Profile.objects.get_or_create(user=admin_user)
        profile.role = 'admin'
        profile.save()
        print(f'✅ Superuser {admin_username} created successfully')
    else:
        print(f'ℹ️ Superuser {admin_username} already exists')
except Exception as e:
    print(f'❌ Error creating admin user: {e}')

operario_username = os.environ.get('OPERARIO_USERNAME', 'operario')
operario_email = os.environ.get('OPERARIO_EMAIL', 'operario@textilapp.com')
operario_password = os.environ.get('OPERARIO_PASSWORD', 'operario123')

try:
    if not User.objects.filter(username=operario_username).exists():
        operario_user = User.objects.create_user(
            username=operario_username,
            email=operario_email,
            password=operario_password,
            first_name='Demo',
            last_name='Operario'
        )
        profile, created = Profile.objects.get_or_create(user=operario_user)
        profile.role = 'operario'
        profile.save()
        print(f'✅ Demo operario {operario_username} created successfully')
    else:
        print(f'ℹ️ Operario {operario_username} already exists')
except Exception as e:
    print(f'❌ Error creating operario user: {e}')
"

echo ✅ Initialization complete!
echo 🌐 Starting development server...
python manage.py runserver