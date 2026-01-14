# Quick Reference: Database Persistence Layer

## Start Services

```powershell
# Start all containers
cd "D:\cdc test"
docker-compose up -d

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View logs
docker logs postgres-management
docker logs redis
```

## Database Access

```powershell
# Connect to database
docker exec -it postgres-management psql -U cdc_user -d cdc_management

# List tables
\dt

# View table structure
\d pipelines
\d connections

# Check data
SELECT * FROM connections;
SELECT * FROM pipelines;
```

## Run Migrations

```powershell
cd "D:\cdc test"

# Create new migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Rollback one migration
python -m alembic downgrade -1

# View migration history
python -m alembic history
```

## Test Database

```powershell
# Test connectivity
python test_db_connection.py

# Test CRUD operations
python test_database_crud.py

# Initialize database
python init_db.py
```

## Python Usage

```python
from ingestion.database import SessionLocal
from ingestion.database.models_db import ConnectionModel, PipelineModel

# Create session
session = SessionLocal()

try:
    # Create
    conn = ConnectionModel(
        id=str(uuid.uuid4()),
        name="My Connection",
        connection_type="source",
        database_type="postgresql",
        host="localhost",
        port=5432,
        database="mydb",
        username="user",
        password="pass"
    )
    session.add(conn)
    session.commit()
    
    # Read
    connections = session.query(ConnectionModel).all()
    
    # Update
    conn.host = "newhost"
    session.commit()
    
    # Delete
    session.delete(conn)
    session.commit()
    
finally:
    session.close()
```

## Important Ports

- **5434** - PostgreSQL (cdc_management database)
- **6379** - Redis
- **8083** - Kafka Connect
- **9092** - Kafka
- **2181** - Zookeeper

## Enum Values (Use .value with strings)

```python
from ingestion.database.models_db import (
    ConnectionType, DatabaseType, PipelineMode,
    PipelineStatus, FullLoadStatus, CDCStatus
)

# Correct usage
connection_type="source"  # or ConnectionType.SOURCE.value
database_type="postgresql"  # or DatabaseType.POSTGRESQL.value
mode="full_load_and_cdc"  # or PipelineMode.FULL_LOAD_AND_CDC.value
```

## Connection String

```
postgresql://cdc_user:cdc_password@localhost:5434/cdc_management
```

## Troubleshooting

### Cannot connect to database
```powershell
# Check if container is running
docker ps | Select-String "postgres-management"

# Check logs
docker logs postgres-management

# Restart container
docker restart postgres-management
```

### Port already in use
```powershell
# Find process using port
netstat -ano | Select-String "5434"

# Stop conflicting service or change port in docker-compose.yml
```

### Reset database
```powershell
# Stop and remove container + volume
docker stop postgres-management
docker rm postgres-management
docker volume rm cdctest_postgres-management-data

# Recreate
docker-compose up -d postgres-management

# Run migrations
python init_db.py
```

## Key Files

- **docker-compose.yml** - Container configuration
- **alembic.ini** - Migration configuration
- **alembic/env.py** - Migration environment
- **ingestion/database/models_db.py** - ORM models
- **ingestion/database/session.py** - Database session
- **env.example** - Environment template
