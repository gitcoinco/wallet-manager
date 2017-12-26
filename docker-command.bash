#!/bin/bash

cd app

# Check whether or not the .env file exists. If not, create it.
if [ ! -f app/.env ]; then
    cp app/local.env.dist app/.env
fi

# Provision the Django test environment.
python manage.py createcachetable
python manage.py collectstatic --noinput -i other
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
