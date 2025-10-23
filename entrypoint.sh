#!/bin/bash
set -e

if [ "$DJANGO_SUPERUSER_CREATE" = "true" ]; then
    echo "👤 Checking if superuser '${DJANGO_SUPERUSER_USERNAME}' exists..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME}"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email="${DJANGO_SUPERUSER_EMAIL}",
        password="${DJANGO_SUPERUSER_PASSWORD}"
    )
    print(f"✅ Superuser '{username}' created.")
else:
    print(f"ℹ️ Superuser '{username}' already exists.")
END
fi

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django..."
exec "$@"
