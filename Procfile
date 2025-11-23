web: gunicorn config.wsgi --log-file -
release: python manage.py migrate --noinput && python create_prod_superuser.py
