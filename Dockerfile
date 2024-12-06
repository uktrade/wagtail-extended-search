FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /
RUN git clone https://github.com/wagtail/bakerydemo.git --config core.autocrlf=input

WORKDIR /bakerydemo
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install debugpy

# Fix Bakerydemo's urllib3 version
RUN pip uninstall urllib3 requests -y
RUN pip install requests

COPY . /package
RUN pip install -e /package

# Add custom environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=bakerydemo.settings.production DJANGO_DEBUG=off

# Call collectstatic with dummy environment variables:
RUN DATABASE_URL=postgres://none REDIS_URL=none python manage.py collectstatic --noinput

# make sure static files are writable by uWSGI process
RUN mkdir -p /bakerydemo/bakerydemo/media/images && mkdir -p /bakerydemo/bakerydemo/media/original_images && chown -R 1000:2000 /bakerydemo/bakerydemo/media

# mark the destination for images as a volume
VOLUME ["/bakerydemo/bakerydemo/media/images/"]
