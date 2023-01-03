#!/bin/sh

# Check if autossh is installed
if ! which autossh > /dev/null; then
    # Install autossh
    apk update
    apk add --no-cache autossh
    # shell script for ssh port forwarding
    mkdir -p ~/.ssh
    ssh-keyscan -H ${SSH_HOST} > ~/.ssh/known_hosts
    chmod 400 ${SSH_PEM_KEY}
fi

autossh -i ${SSH_PEM_KEY} -M 33306 -4fNL ${DATABASE_PORT}:${RDS_HOST}:${DATABASE_PORT} ${SSH_USER}@${SSH_HOST}

python manage.py migrate
python manage.py runserver 0.0.0.0:8000