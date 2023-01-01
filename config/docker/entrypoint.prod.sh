#!/bin/sh

python manage.py collectstatic --no-input
python manage.py migrate
#python manage.py loaddata init_data.yaml

exec "$@"