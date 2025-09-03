@echo off
echo Checking container status...
echo =============================
docker ps
echo.
echo Checking API logs...
echo =============================
docker compose logs api --tail=20
echo.
echo Checking database logs...
echo =============================
docker compose logs db --tail=10
echo.
echo Testing API endpoint...
echo =============================
curl -v http://localhost:8000/health
echo.