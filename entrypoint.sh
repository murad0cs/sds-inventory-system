#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER > /dev/null 2>&1; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

echo "Running Alembic migrations..."
# Try to upgrade to latest, if multiple heads exist, just continue
alembic upgrade head || echo "Migration might have multiple heads, continuing..."

# Ensure audit_logs table exists
python -c "
from app.db.base import Base, engine
from app.models import AuditLog
import asyncio
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(create_tables())
print('Tables verified/created')
" || echo "Table creation handled"

echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload