bakery-init:
	docker compose build
	docker compose up -d
	docker compose run --rm app ./manage.py migrate
	docker compose run --rm app ./manage.py load_initial_data
	docker compose run --rm app ./manage.py update_index

bakery-refresh:
	docker compose build
	docker compose down app
	docker compose up -d

bakery-bash:
	docker compose run --rm app bash

bakery-down:
	docker compose down
	rm -rf media

# build-package:
# 	poetry build

# push-pypi-test:
# 	poetry publish -r test-pypi

# push-pypi:
# 	poetry publish
