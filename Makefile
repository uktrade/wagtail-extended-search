bakery-setup:
	git clone https://github.com/wagtail/bakerydemo.git --config core.autocrlf=input

docker-compose = docker compose -f ./bakerydemo/docker-compose.yml -f ./bakerydemo-overrides/docker-compose.wes.yml

bakery-init:
	cp ./bakerydemo-overrides/settings/wes.py ./bakerydemo/bakerydemo/settings/wes.py
	$(docker-compose) up --build -d
	$(docker-compose) run app /venv/bin/python manage.py migrate
	$(docker-compose) run app /venv/bin/python manage.py load_initial_data

bakery-start:
	$(docker-compose) up

bakery-stop:
	$(docker-compose) stop

bakery-down:
	$(docker-compose) down

bakery-clear:
	$(docker-compose) down
	rm -rf bakerydemo

bakery-bash:
	$(docker-compose) run app bash

build-package:
	poetry build

push-pypi-test:
	poetry publish -r test-pypi

push-pypi:
	poetry publish
