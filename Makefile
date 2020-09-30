build:
	docker-compose build

up:
	docker-compose up -d redis-db elevator controller
	docker-compose logs -f elevator

down:
	docker-compose stop

logs:
	docker-compose logs --tail 30 -f elevator

test:
	docker-compose run elevator pytest -v tests/test_elevator.py
