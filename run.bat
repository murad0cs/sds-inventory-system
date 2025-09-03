@echo off
echo Building and starting SDS Chemical Inventory System...
echo ===========================================

docker compose down -v 2>nul

echo Building Docker images...
docker compose build

echo Starting services...
docker compose up -d

echo Waiting for API to be ready...
timeout /t 10 /nobreak > nul

curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo.
    echo ===========================================
    echo API is ready and available at http://localhost:8000
    echo API Documentation: http://localhost:8000/docs
    echo ===========================================
    echo.
    echo To view logs: docker compose logs -f
    echo To stop services: docker compose down
) else (
    echo.
    echo API may still be starting. Please wait a moment and check:
    echo http://localhost:8000/docs
    echo.
    echo To view logs: docker compose logs -f
)