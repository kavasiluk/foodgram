#!/bin/sh

./wait_for_db.sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
