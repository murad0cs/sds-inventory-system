# SDS Chemical Inventory System - Setup Guide

## Project Overview

This project implements a Safety Data Sheet (SDS) Chemical Inventory and Reporting System using FastAPI with hybrid database access (SQLAlchemy ORM + asyncpg direct queries).

## Setup Instructions

### Method 1: Quick Start with Docker (Recommended)

**Time Required: ~2 minutes**

1. **Prerequisites**
   - Docker Desktop installed and running
   - Git (optional, for cloning)

2. **Run the Application**
   ```bash
   # Navigate to project directory
   cd sds_inventory_system
   
   # Make the script executable (Unix/Mac/WSL)
   chmod +x run.sh
   
   # Run the application
   ./run.sh
   ```

3. **Verify Installation**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Run tests: `python test_api.py`

### Method 2: Local Development Setup

**Time Required: ~10 minutes**

1. **Install Python 3.13 with Conda**
   ```bash
   # Create environment from file
   conda env create -f environment.yml
   
   # Activate environment
   conda activate sds_inventory
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL Database**
   
   Option A - Using Docker:
   ```bash
   docker run -d \
     --name sds_postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=sds_inventory \
     -p 5432:5432 \
     postgres:16-alpine
   ```
   
   Option B - Using existing PostgreSQL:
   - Create database: `CREATE DATABASE sds_inventory;`
   - Update `.env` file with your credentials

4. **Configure Environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your database credentials
   # For local PostgreSQL, use DATABASE_HOST=localhost
   ```

5. **Run Database Migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the Application**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Method 3: Azure PostgreSQL Setup

1. **Create Azure PostgreSQL Instance**
   - Use Azure Portal or CLI to create PostgreSQL server
   - Note down server name, username, and password

2. **Update Configuration**
   ```bash
   # Edit .env file
   DATABASE_HOST=your-server.postgres.database.azure.com
   DATABASE_PORT=5432
   DATABASE_NAME=sds_inventory
   DATABASE_USER=your-username@your-server
   DATABASE_PASSWORD=your-password
   ENVIRONMENT=azure
   ```

3. **Configure Firewall**
   - Add your IP address to Azure PostgreSQL firewall rules
   - Enable "Allow access to Azure services" if needed

4. **Run Application**
   - Follow Method 1 (Docker) or Method 2 (Local) with Azure credentials

## Dependencies

### Python Packages
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **sqlalchemy**: ORM
- **alembic**: Database migrations
- **asyncpg**: Async PostgreSQL driver
- **pydantic**: Data validation
- **python-dotenv**: Environment management
- **psycopg2-binary**: PostgreSQL adapter

### System Requirements
- Python 3.13
- PostgreSQL 16+
- Docker & Docker Compose (for containerized setup)

## Verification Steps

1. **Check API Status**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "healthy"}
   ```

2. **Test Database Connection**
   ```bash
   curl http://localhost:8000/api/v1/chemicals/
   # Expected: [] (empty array initially)
   ```

3. **Run Test Suite**
   ```bash
   python test_api.py
   # Should complete all 8 tests successfully
   ```

## Common Issues and Solutions

### Issue 1: Port 8000 Already in Use
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Unix/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

### Issue 2: Database Connection Failed
**Solution:**
- Verify PostgreSQL is running: `docker ps`
- Check credentials in `.env` file
- For Docker, use `DATABASE_HOST=db`
- For local, use `DATABASE_HOST=localhost`

### Issue 3: Migration Errors
**Solution:**
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head

# Or recreate database
docker-compose down -v
docker-compose up -d
```

### Issue 4: Import Errors
**Solution:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.13
```

## Directory Structure

```
sds_inventory_system/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   └── main.py            # FastAPI app
├── alembic/               # Database migrations
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Container definition
├── entrypoint.sh         # Container startup
├── run.sh               # Quick start script
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
└── test_api.py         # API tests
```

## Next Steps

1. Access API documentation at http://localhost:8000/docs
2. Run the test suite to verify functionality
3. Explore the hybrid database implementation
4. Review the code structure for best practices

## Support

For issues or questions about this test project, please refer to the included documentation or contact the development team.