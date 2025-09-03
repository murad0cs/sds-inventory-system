@echo off
echo Checking the last 50 lines of API logs...
echo =========================================
docker compose logs api --tail=50
echo.
echo =========================================
echo Checking if tables exist in database...
docker compose exec db psql -U postgres -d sds_inventory -c "\dt"
echo.
echo =========================================
echo Trying to run migrations manually...
docker compose exec api alembic upgrade head