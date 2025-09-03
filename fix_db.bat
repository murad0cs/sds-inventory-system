@echo off
echo Running database migrations manually...
echo =====================================
docker compose exec api alembic upgrade head

echo.
echo Creating initial migration if needed...
echo =====================================
docker compose exec api alembic revision --autogenerate -m "Initial migration"
docker compose exec api alembic upgrade head

echo.
echo Checking database tables...
echo =====================================
docker compose exec db psql -U postgres -d sds_inventory -c "\dt"

echo.
echo Testing API endpoint...
echo =====================================
curl -X GET http://localhost:8000/api/v1/chemicals/

echo.
echo.
echo If you still see errors, restart the API:
echo docker compose restart api