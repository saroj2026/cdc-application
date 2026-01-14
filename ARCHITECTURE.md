# CDC Pipeline System - Complete Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow & Process Architecture](#data-flow--process-architecture)
5. [Technology Stack](#technology-stack)
6. [Database Schema](#database-schema)
7. [API Architecture](#api-architecture)
8. [Frontend Architecture](#frontend-architecture)
9. [CDC Pipeline Lifecycle](#cdc-pipeline-lifecycle)
10. [Infrastructure & Deployment](#infrastructure--deployment)
11. [Security & Authentication](#security--authentication)
12. [Monitoring & Alerting](#monitoring--alerting)

---

## System Overview

### What is This System?

A **production-ready Change Data Capture (CDC) platform** that provides automated real-time data replication between databases. The system automatically creates and manages CDC pipelines using Kafka Connect, Debezium, and JDBC Sink Connectors.

### Key Capabilities

- **Zero-Configuration CDC**: Users provide database credentials, system handles all Kafka configuration
- **Multi-Database Support**: PostgreSQL, SQL Server, MySQL, S3
- **Full Load + CDC**: Initial data synchronization with continuous change capture
- **Real-Time Replication**: Sub-second latency for data changes
- **Web-Based Management**: Full-featured UI for pipeline management
- **Enterprise Features**: Authentication, monitoring, alerting, data quality checks

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Web Browser    │  │   REST API       │  │   CLI Tools      │ │
│  │   (Next.js UI)   │  │   Clients        │  │   (Python)       │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
└───────────┼──────────────────────┼──────────────────────┼───────────┘
            │                      │                      │
            │ HTTP/HTTPS           │ HTTP/HTTPS           │
            ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Port 8000)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │   API Routes  │  │   Services    │  │   Managers   │   │   │
│  │  │   - Auth      │  │   - Pipeline  │  │   - CDC      │   │   │
│  │  │   - Pipeline  │  │   - Connection│  │   - Recovery │   │   │
│  │  │   - Connection│  │   - Discovery │  │   - Monitoring│  │   │
│  │  │   - Monitoring│  │   - Schema    │  │              │   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │   │
│  └─────────┼─────────────────┼─────────────────┼─────────────┘   │
│            │                  │                  │                  │
│  ┌─────────┴─────────────────┴─────────────────┴──────────────┐  │
│  │              Database Layer (PostgreSQL)                    │  │
│  │  - Connections, Pipelines, Users, Metrics, Alerts            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
            │
            │ Kafka Connect REST API
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    KAFKA INFRASTRUCTURE LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Zookeeper  │  │    Kafka     │  │ Kafka Connect │           │
│  │   (Port 2181)│  │  (Port 9092) │  │  (Port 8083)  │           │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘           │
└────────────────────────────┼─────────────────┼─────────────────────┘
                              │                 │
                    ┌─────────┴─────────┐      │
                    │                   │      │
            ┌───────▼────────┐  ┌───────▼────────┐
            │  Debezium     │  │  JDBC Sink    │
            │  Connector    │  │  Connector    │
            │  (Source)     │  │  (Target)     │
            └───────┬────────┘  └───────┬────────┘
                    │                   │
                    │ WAL/Changes       │ SQL Inserts/Updates
                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                               │
│  ┌──────────────────┐                    ┌──────────────────┐    │
│  │  Source Database │                    │  Target Database │    │
│  │  - PostgreSQL    │                    │  - SQL Server    │    │
│  │  - SQL Server    │                    │  - PostgreSQL   │    │
│  │  - MySQL         │                    │  - MySQL        │    │
│  │  - S3            │                    │  - S3           │    │
│  └──────────────────┘                    └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Backend Components

#### 1. **API Layer** (`ingestion/api.py`)
- **FastAPI Application**: Main REST API server
- **Endpoints**:
  - Authentication: `/api/v1/auth/*`
  - Connections: `/api/v1/connections/*`
  - Pipelines: `/api/v1/pipelines/*`
  - Monitoring: `/api/v1/monitoring/*`
  - Discovery: `/api/v1/discovery/*`
- **Middleware**: CORS, Authentication, Error Handling

#### 2. **Service Layer**

**Pipeline Service** (`ingestion/pipeline_service.py`)
- Pipeline CRUD operations
- Pipeline lifecycle management
- Status tracking

**Connection Service** (`ingestion/connection_service.py`)
- Connection management
- Connection testing
- Database connector instantiation

**Discovery Service** (`ingestion/discovery_service.py`)
- Database schema discovery
- Table enumeration
- Column metadata extraction

**Schema Service** (`ingestion/schema_service.py`)
- Schema comparison
- Schema migration planning
- Type mapping

#### 3. **Manager Layer**

**CDC Manager** (`ingestion/cdc_manager.py`)
- **Core Orchestrator**: Main pipeline execution engine
- Responsibilities:
  - Pipeline creation and configuration
  - Full load execution
  - CDC connector deployment
  - Status monitoring
  - Error recovery

**Recovery Manager** (`ingestion/recovery.py`)
- Pipeline failure recovery
- Connector restart logic
- Data consistency checks

**CDCMonitor** (`ingestion/monitoring.py`)
- Real-time pipeline monitoring
- Health checks
- Performance metrics

#### 4. **Configuration Generators**

**Debezium Config Generator** (`ingestion/debezium_config.py`)
- Auto-generates Debezium source connector configurations
- Handles replication slots, publications, table filters
- Snapshot mode configuration

**Sink Config Generator** (`ingestion/sink_config.py`)
- Auto-generates JDBC Sink connector configurations
- Table mapping, transforms, schema settings
- Error handling configuration

#### 5. **Connectors** (`ingestion/connectors/`)

**Base Connector** (`base_connector.py`)
- Abstract base class for all database connectors
- Common interface: connect, disconnect, test, query

**PostgreSQL Connector** (`postgresql.py`)
- PostgreSQL-specific operations
- WAL/LSN management
- Publication and replication slot management
- Full load data transfer

**SQL Server Connector** (`sqlserver.py`)
- SQL Server-specific operations
- Schema creation
- Data type mapping

#### 6. **Infrastructure Clients**

**Kafka Connect Client** (`ingestion/kafka_connect_client.py`)
- REST API client for Kafka Connect
- Connector CRUD operations
- Status monitoring
- Error handling

#### 7. **Monitoring & Quality**

**Metrics Collector** (`ingestion/metrics_collector.py`)
- Pipeline performance metrics
- Throughput, lag, error rates
- Time-series data collection

**Lag Monitor** (`ingestion/lag_monitor.py`)
- Consumer lag monitoring
- Offset tracking
- Alert generation

**Data Quality Monitor** (`ingestion/data_quality.py`)
- Data validation
- Schema drift detection
- Data consistency checks

**Alert Engine** (`ingestion/alerting/alert_engine.py`)
- Alert rule evaluation
- Multi-channel notifications
- Alert history tracking

### Frontend Components

#### 1. **Application Structure** (`frontend/app/`)

**Pages**:
- `/` - Landing/Dashboard
- `/auth/login` - User authentication
- `/auth/signup` - User registration
- `/connections` - Connection management
- `/pipelines` - Pipeline management
- `/pipelines/[id]/monitor` - Pipeline monitoring
- `/monitoring` - System-wide monitoring
- `/analytics` - Analytics dashboard
- `/governance` - Data governance
- `/settings` - User settings

#### 2. **Components** (`frontend/components/`)

**UI Components** (`ui/`):
- Reusable shadcn/ui components
- Forms, tables, dialogs, cards

**Feature Components**:
- `connections/` - Connection management UI
- `pipelines/` - Pipeline management UI
- `dashboard/` - Dashboard widgets
- `alerts/` - Alert management
- `governance/` - Governance tools

**Layout Components** (`layout/`):
- Sidebar navigation
- Header/topbar
- Main layout wrapper

#### 3. **State Management**

**Context Providers**:
- `theme-context.tsx` - Theme management
- `sidebar-context.tsx` - Sidebar state

**Hooks**:
- `useAuth.ts` - Authentication state

**API Integration**:
- Axios-based API client
- RESTful API communication

---

## Data Flow & Process Architecture

### 1. Pipeline Creation Flow

```
User Input (Credentials)
    │
    ▼
┌─────────────────────────────────────┐
│  API: POST /api/v1/pipelines        │
│  - Validates input                  │
│  - Creates Connection objects       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  PipelineService.create_pipeline()   │
│  - Validates connections            │
│  - Creates PipelineModel            │
│  - Stores in database               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  CDCManager.start_pipeline()        │
│  - Checks pipeline mode            │
│  - Executes full load (if enabled) │
│  - Generates Debezium config        │
│  - Generates Sink config           │
│  - Deploys connectors              │
└──────────────┬──────────────────────┘
               │
               ▼
         Pipeline RUNNING
```

### 2. Full Load Process

```
┌─────────────────────────────────────┐
│  Full Load Initiated                │
│  - Pipeline.enable_full_load=true  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  DataTransfer.transfer_data()       │
│  - Connects to source DB            │
│  - Discovers schema                 │
│  - Creates target schema             │
│  - Transfers data in batches        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Capture LSN                        │
│  - Gets current WAL position       │
│  - Stores in pipeline.full_load_lsn│
└──────────────┬──────────────────────┘
               │
               ▼
         Full Load COMPLETED
```

### 3. CDC Replication Flow

```
┌─────────────────────────────────────┐
│  Source Database (PostgreSQL)      │
│  - Data change occurs               │
│  - WAL entry created                │
└──────────────┬──────────────────────┘
               │
               │ Logical Replication
               ▼
┌─────────────────────────────────────┐
│  Debezium Connector                 │
│  - Reads from WAL                   │
│  - Extracts change event            │
│  - Transforms to Kafka message      │
└──────────────┬──────────────────────┘
               │
               │ Kafka Message
               ▼
┌─────────────────────────────────────┐
│  Kafka Topic                        │
│  - {pipeline}.{schema}.{table}     │
│  - Message queued                   │
└──────────────┬──────────────────────┘
               │
               │ Consume Message
               ▼
┌─────────────────────────────────────┐
│  JDBC Sink Connector                │
│  - Consumes from Kafka              │
│  - Extracts data (ExtractField)     │
│  - Maps to target schema            │
└──────────────┬──────────────────────┘
               │
               │ SQL INSERT/UPDATE
               ▼
┌─────────────────────────────────────┐
│  Target Database (SQL Server)       │
│  - Data replicated                  │
└─────────────────────────────────────┘
```

### 4. Configuration Generation Flow

```
User Credentials
    │
    ▼
┌─────────────────────────────────────┐
│  DebeziumConfigGenerator            │
│  generate_source_config()           │
│  - Database connection details     │
│  - Replication slot name            │
│  - Publication configuration        │
│  - Table include list               │
│  - Snapshot mode                    │
│  - Schema settings                  │
│  → Returns complete JSON config     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  SinkConfigGenerator                │
│  generate_sink_config()             │
│  - JDBC connection URL              │
│  - Topic names                      │
│  - Table name mapping               │
│  - Transform config (ExtractField)  │
│  - Schema converter                 │
│  - Error handling                   │
│  → Returns complete JSON config     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  KafkaConnectClient                 │
│  create_connector()                │
│  - POST to Kafka Connect REST API   │
│  - Deploys connector                │
│  - Monitors status                  │
└─────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 15+
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **HTTP Client**: requests
- **Logging**: python-json-logger

### Frontend
- **Framework**: Next.js 16.0+
- **Language**: TypeScript 5+
- **UI Library**: React 19.2+
- **Styling**: Tailwind CSS 4.1+
- **Components**: shadcn/ui (Radix UI)
- **State**: React Context, Redux Toolkit
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod

### Infrastructure
- **Message Broker**: Apache Kafka 3.6+
- **CDC Engine**: Debezium 2.5+
- **Connect Framework**: Kafka Connect
- **Sink Connector**: Confluent JDBC Sink
- **Container Orchestration**: Docker Compose
- **Cache**: Redis 7+

### Database Support
- **Source**: PostgreSQL, SQL Server, MySQL
- **Target**: SQL Server, PostgreSQL, MySQL, S3

---

## Database Schema

### Core Tables

#### `connections`
Stores database connection configurations.

```sql
- id (UUID, PK)
- name (VARCHAR)
- connection_type (ENUM: source, target)
- database_type (ENUM: postgresql, sqlserver, mysql, s3)
- host, port, database, username, password
- schema, additional_config (JSON)
- is_active, last_tested_at, last_test_status
- created_at, updated_at, deleted_at
```

#### `pipelines`
Stores CDC pipeline configurations and status.

```sql
- id (UUID, PK)
- name (VARCHAR, UNIQUE)
- source_connection_id (FK → connections)
- target_connection_id (FK → connections)
- source_database, source_schema, source_tables (JSON)
- target_database, target_schema, target_tables (JSON)
- mode (ENUM: full_load_only, cdc_only, full_load_and_cdc)
- enable_full_load, full_load_status, full_load_lsn
- cdc_status, status
- debezium_connector_name, sink_connector_name
- kafka_topics (JSON)
- debezium_config, sink_config (JSON)
- auto_create_target, target_table_mapping (JSON)
- created_at, updated_at, deleted_at
```

#### `users`
User authentication and authorization.

```sql
- id (UUID, PK)
- email (VARCHAR, UNIQUE)
- full_name, hashed_password
- role_name, is_active, is_superuser
- created_at, updated_at
```

#### `pipeline_runs`
Execution history for pipelines.

```sql
- id (UUID, PK)
- pipeline_id (FK → pipelines)
- run_type, status
- started_at, completed_at
- rows_processed, errors_count, error_message
- run_metadata (JSON)
```

#### `pipeline_metrics`
Time-series metrics for pipelines.

```sql
- id (UUID, PK)
- pipeline_id (FK → pipelines)
- timestamp
- throughput_events_per_sec, lag_seconds
- error_count, bytes_processed
- source_offset, target_offset
- connector_status (JSON)
```

#### `connection_tests`
Connection test history.

```sql
- id (UUID, PK)
- connection_id (FK → connections)
- test_status, response_time_ms, error_message
- tested_at
```

#### `alert_rules`
Alert configuration.

```sql
- id (UUID, PK)
- name, metric, condition, threshold
- duration_seconds, severity, channels (JSON)
- enabled, created_at, updated_at
```

#### `alert_history`
Alert event log.

```sql
- id (UUID, PK)
- rule_id (FK → alert_rules)
- pipeline_id, status, message
- triggered_at, resolved_at, acknowledged_at
- alert_metadata (JSON)
```

#### `audit_logs`
Complete audit trail.

```sql
- id (UUID, PK)
- entity_type, entity_id, action
- user_id, old_values, new_values (JSON)
- timestamp
```

---

## API Architecture

### RESTful API Design

**Base URL**: `http://localhost:8000/api/v1`

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Current user info

### Connection Endpoints
- `GET /connections` - List connections
- `POST /connections` - Create connection
- `GET /connections/{id}` - Get connection
- `PUT /connections/{id}` - Update connection
- `DELETE /connections/{id}` - Delete connection
- `POST /connections/{id}/test` - Test connection

### Pipeline Endpoints
- `GET /pipelines` - List pipelines
- `POST /pipelines` - Create pipeline
- `GET /pipelines/{id}` - Get pipeline
- `PUT /pipelines/{id}` - Update pipeline
- `DELETE /pipelines/{id}` - Delete pipeline
- `POST /pipelines/{id}/start` - Start pipeline
- `POST /pipelines/{id}/stop` - Stop pipeline
- `GET /pipelines/{id}/status` - Get pipeline status

### Discovery Endpoints
- `POST /discovery/discover` - Discover database schema
- `GET /discovery/tables` - List tables
- `GET /discovery/schemas` - List schemas

### Monitoring Endpoints
- `GET /monitoring/pipelines` - Pipeline health
- `GET /monitoring/metrics` - System metrics
- `GET /monitoring/lag` - Consumer lag

---

## Frontend Architecture

### Application Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/             # Authentication pages
│   ├── connections/        # Connection management
│   ├── pipelines/          # Pipeline management
│   ├── monitoring/         # Monitoring dashboard
│   └── api/                # API routes (proxy)
├── components/             # React components
│   ├── ui/                 # Reusable UI components
│   ├── connections/        # Connection components
│   ├── pipelines/         # Pipeline components
│   └── layout/             # Layout components
├── contexts/               # React contexts
├── hooks/                  # Custom hooks
└── public/                 # Static assets
```

### State Management

- **Server State**: React Query / SWR (API data)
- **Client State**: React Context (theme, auth)
- **Form State**: React Hook Form
- **Global State**: Redux Toolkit (if needed)

### Routing

- **File-based routing**: Next.js App Router
- **Dynamic routes**: `/pipelines/[id]/monitor`
- **API routes**: `/api/auth/*` (proxy to backend)

---

## CDC Pipeline Lifecycle

### Pipeline States

```
STOPPED → STARTING → RUNNING → STOPPING → STOPPED
   │         │          │          │
   │         │          │          └──→ ERROR
   │         │          │
   │         │          └──→ ERROR
   │         │
   │         └──→ ERROR
   │
   └──→ ERROR
```

### Lifecycle Stages

#### 1. **Creation**
- User provides credentials
- System validates connections
- Pipeline object created
- Stored in database

#### 2. **Configuration**
- Debezium config generated
- Sink config generated
- Connector names assigned
- Kafka topics identified

#### 3. **Full Load** (if enabled)
- Initial data synchronization
- Schema creation
- Data transfer in batches
- LSN captured after completion

#### 4. **CDC Activation**
- Debezium connector deployed
- Replication slot created/used
- Sink connector deployed
- Real-time replication starts

#### 5. **Running**
- Continuous change capture
- Real-time replication
- Metrics collection
- Health monitoring

#### 6. **Stopping**
- Connectors paused
- Resources cleaned up
- Status updated

#### 7. **Deletion**
- Connectors removed
- Pipeline marked as deleted
- Audit log created

---

## Infrastructure & Deployment

### Docker Compose Services

```yaml
Services:
  - zookeeper:      # Kafka coordination (Port 2181)
  - kafka:         # Message broker (Port 9092)
  - kafka-connect: # Connector framework (Port 8083)
  - postgres-management: # Application database (Port 5434)
  - redis:         # Cache/session store (Port 6379)
```

### Network Architecture

```
┌─────────────────────────────────────────┐
│         Docker Network                   │
│  ┌──────────┐  ┌──────────┐            │
│  │ Zookeeper│  │  Kafka   │            │
│  └────┬─────┘  └────┬─────┘            │
│       │             │                   │
│       └──────┬──────┘                   │
│              │                          │
│       ┌─────▼──────┐                   │
│       │Kafka Connect│                  │
│       └─────────────┘                   │
└─────────────────────────────────────────┘
              │
              │ REST API
              ▼
┌─────────────────────────────────────────┐
│      Host Network                       │
│  ┌──────────┐  ┌──────────┐            │
│  │ Backend  │  │ Frontend │            │
│  │ :8000    │  │ :3000    │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

### Deployment Architecture

**Development**:
- Backend: `python -m ingestion.api`
- Frontend: `npm run dev`
- Infrastructure: `docker-compose up`

**Production** (Recommended):
- Backend: Gunicorn/Uvicorn with multiple workers
- Frontend: Next.js production build
- Infrastructure: Kubernetes or Docker Swarm
- Database: Managed PostgreSQL (RDS, Azure, etc.)
- Kafka: Managed Kafka service (Confluent Cloud, etc.)

---

## Security & Authentication

### Authentication Flow

```
1. User submits credentials
   │
   ▼
2. Backend validates credentials
   │
   ▼
3. JWT token generated
   │
   ▼
4. Token stored in HTTP-only cookie / localStorage
   │
   ▼
5. Subsequent requests include token
   │
   ▼
6. Backend validates token
   │
   ▼
7. Request processed
```

### Authorization

**Roles**:
- `admin`: Full system access
- `operator`: Pipeline management
- `viewer`: Read-only access
- `user`: Basic access

**Permissions**:
- Connection management (admin, operator)
- Pipeline creation (admin, operator)
- Pipeline monitoring (all roles)
- User management (admin only)

### Security Features

- **Password Hashing**: bcrypt
- **JWT Tokens**: HS256 algorithm
- **CORS**: Configured for frontend origins
- **Input Validation**: Pydantic models
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: React auto-escaping

---

## Monitoring & Alerting

### Metrics Collected

**Pipeline Metrics**:
- Throughput (events/second)
- Consumer lag (seconds)
- Error count
- Bytes processed
- Connector status

**System Metrics**:
- API response times
- Database connection pool
- Kafka consumer groups
- Resource utilization

### Alerting System

**Alert Rules**:
- Metric-based thresholds
- Duration-based conditions
- Multi-channel notifications

**Alert Channels**:
- Email
- Webhook
- In-app notifications

**Alert Types**:
- Pipeline failure
- High lag
- Error rate threshold
- Connection failure

### Monitoring Dashboard

**Real-time Views**:
- Pipeline health status
- Throughput graphs
- Lag visualization
- Error logs
- System resource usage

---

## Key Design Principles

### 1. **Automation First**
- Zero manual Kafka configuration
- Automatic connector deployment
- Self-healing capabilities

### 2. **Extensibility**
- Plugin-based connector architecture
- Configurable transformations
- Custom alert rules

### 3. **Reliability**
- Error recovery mechanisms
- Data consistency checks
- Health monitoring

### 4. **Scalability**
- Stateless API design
- Horizontal scaling support
- Efficient resource usage

### 5. **User Experience**
- Simple credential-based setup
- Comprehensive monitoring
- Intuitive web interface

---

## Future Enhancements

### Planned Features
- [ ] Multi-tenant support
- [ ] Advanced data transformations
- [ ] Schema evolution handling
- [ ] Backup and restore
- [ ] Performance optimization
- [ ] Additional database connectors
- [ ] Real-time data quality checks
- [ ] Advanced analytics

---

## Conclusion

This CDC Pipeline System provides a complete, production-ready solution for automated real-time data replication. The architecture is designed for:

- **Ease of Use**: Simple credential-based setup
- **Reliability**: Robust error handling and recovery
- **Scalability**: Horizontal scaling capabilities
- **Observability**: Comprehensive monitoring and alerting
- **Extensibility**: Plugin-based architecture

The system automatically handles all complex Kafka configuration, allowing users to focus on their data replication needs rather than infrastructure management.

