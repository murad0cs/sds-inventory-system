@echo off
echo Stopping all containers...
docker stop a8bb1ab78822 2>nul
docker rm a8bb1ab78822 2>nul
docker compose down

echo.
echo Rebuilding and starting with proper configuration...
docker compose up --build -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak > nul

echo.
echo Checking status...
docker ps
echo.
echo Testing API...
curl http://localhost:8000/health

echo.
echo If API is not responding, check logs with:
echo docker compose logs api