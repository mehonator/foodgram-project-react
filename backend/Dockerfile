FROM python:3.8.5

WORKDIR /code
COPY requirements.txt ./

RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn backend.wsgi:application --env DJANGO_SETTINGS_MODULE=backend.settings.production.py --bind 0.0.0.0:8000 