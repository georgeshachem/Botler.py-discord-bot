fast:
	pipenv run python run.py
migrate:
	pipenv run alembic revision -m "migration" --autogenerate --head head
	pipenv run alembic upgrade head
db:
	docker-compose up -d postgres
bot:
	docker-compose up -d bot
run:
	docker-compose up --build
firstrun:
	pipenv install