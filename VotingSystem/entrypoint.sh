#!/bin/bash

# Apply migrations
python manage.py migrate --settings=VotingSystem.settings.production

# Start Django server
python manage.py runserver 0.0.0.0:8000 --settings=VotingSystem.settings.production
