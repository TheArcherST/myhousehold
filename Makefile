alembic:
	docker compose run --rm tool-alembic $(command)
migrations-run:
	docker compose run --rm tool-alembic upgrade head
migrations-generate:
	docker compose run --rm tool-alembic revision -m $(m) $(msg) $(message) --autogenerate
