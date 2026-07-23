TAIL=100

define set-default-container
	ifndef c
	c = backend
	else ifeq (${c},all)
	override c=
	endif
endef


set-container:
	$(eval $(call set-default-container))
build:
	docker compose -f docker-compose.yaml build
full-build:
	docker compose -f docker-compose.yaml build --no-cache
up:
	docker compose -f docker-compose.yaml up -d
down:
	docker compose -f docker-compose.yaml down
logs: set-container
	docker compose -f docker-compose.yaml logs --tail=$(TAIL) -f $(c)
restart: set-container
	docker compose -f docker-compose.yaml restart $(c)
exec: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash
remove: set-container
	docker compose -f docker-compose.yaml rm -fs $(c)
shell: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'python /app/manage.py shell'
migrate: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'python /app/manage.py migrate'
migrations: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'python /app/manage.py makemigrations'
ruff-check: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'pip install ruff && ruff check'
ruff-format: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'pip install ruff && ruff check --fix --unsafe-fixes && ruff format'
test: set-container
	docker compose -f docker-compose.yaml exec $(c) /bin/bash -c 'cd /app && pytest -vvs'
