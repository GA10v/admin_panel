#!/bin/sh
while ! nc -z $DB_HOST 5432; do sleep 1; done;
python3 manage.py migrate
python3 manage.py createsuperuser --noinput \
                                --username $DJANGO_SUPERUSER_USERNAME \
                                --email $DJANGO_SUPERUSER_EMAIL
python3 manage.py collectstatic --noinput
cd db_init
python3 load_data.py
cd ..
uwsgi --ini uwsgi.ini