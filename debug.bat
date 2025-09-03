@echo off
echo Checking API logs for errors...
echo =====================================
docker compose logs api --tail=50

echo.
echo Checking database connectivity...
echo =====================================
docker compose exec db psql -U postgres -d sds_inventory -c "\dt"

echo.
echo Checking if migrations ran...
echo =====================================
docker compose exec api alembic current