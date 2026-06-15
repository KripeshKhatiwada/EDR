## Phase 4: Database Integration (PostgreSQL)

In this phase, the system was upgraded from in-memory storage to persistent database storage using PostgreSQL and SQLAlchemy.

### What changed
- Added PostgreSQL database for telemetry storage
- Replaced in-memory Python list with database table
- Used SQLAlchemy ORM for models and session handling
- Created a telemetry table to store system metrics
- Updated FastAPI backend to save and fetch data from PostgreSQL

### Architecture
Agent → FastAPI → SQLAlchemy → PostgreSQL

### Stored Data
Each telemetry record includes:
- hostname
- cpu_percent
- memory_percent
- disk_percent

### Result
- Data is now persistent (survives restarts)
- Historical telemetry can be queried
- Backend is now closer to real-world monitoring systems
