up:
	docker compose up --build

down:
	docker compose down

migrate:
	cd apps/api && alembic upgrade head

seed:
	cd apps/api && python scripts/seed_initial_data.py

bootstrap-admin:
	cd apps/api && python scripts/bootstrap_admin.py

test:
	cd apps/api && pytest -q
