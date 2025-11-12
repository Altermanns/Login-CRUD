#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django application with SQLite..."

# Run migrations
echo "📋 Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django application with SQLite..."

# Ensure database file has correct permissions
echo "🔒 Setting database permissions..."
if [ -f "db.sqlite3" ]; then
    chmod 664 db.sqlite3
fi

# Run migrations with error handling
echo "📋 Applying database migrations..."
python manage.py migrate --noinput || {
    echo "❌ Migration failed"
    exit 1
}

# Collect static files with error handling
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    echo "❌ Static file collection failed"
    exit 1
}

# Create default users with better error handling
echo "👥 Creating default users..."
python manage.py shell << 'END' || {
    echo "❌ User creation failed"
    exit 1
}
try:
    from django.contrib.auth.models import User
    from Texcore.models import Profile
    import os

    # Create admin user if not exists
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@textilapp.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    if not User.objects.filter(username=admin_username).exists():
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='Sistema'
        )
        # Ensure profile exists with admin role
        profile, created = Profile.objects.get_or_create(user=admin_user)
        profile.role = 'admin'
        profile.save()
        print(f'✅ Superuser {admin_username} created successfully')
    else:
        print(f'ℹ️ Superuser {admin_username} already exists')

    # Create demo operario if not exists
    operario_username = os.environ.get('OPERARIO_USERNAME', 'operario')
    operario_email = os.environ.get('OPERARIO_EMAIL', 'operario@textilapp.com')
    operario_password = os.environ.get('OPERARIO_PASSWORD', 'operario123')

    if not User.objects.filter(username=operario_username).exists():
        operario_user = User.objects.create_user(
            username=operario_username,
            email=operario_email,
            password=operario_password,
            first_name='Demo',
            last_name='Operario'
        )
        # Ensure profile exists with operario role
        profile, created = Profile.objects.get_or_create(user=operario_user)
        profile.role = 'operario'
        profile.save()
        print(f'✅ Demo operario {operario_username} created successfully')
    else:
        print(f'ℹ️ Operario {operario_username} already exists')
        
except Exception as e:
    print(f"❌ Error during user creation: {e}")
    raise
END

echo "🎉 Initialization complete!"

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn LoginCRUD.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile -