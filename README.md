# EDR Lite – Endpoint Detection & Response System

A full-stack endpoint detection and response (EDR) system that collects real-time system telemetry from monitored hosts, applies rule-based threat detection, and provides a centralized dashboard for security monitoring.

**Status:** Fully functional prototype. Not production-grade. 

---

## What This Project Does

**In plain terms:**

1. An agent runs on a monitored Linux host
2. Every needed(5 or 10) seconds, it collects: CPU, memory, disk, running processes, open ports, file hashes, failed logins
3. It POSTs this data (JSON) to a FastAPI backend
4. The backend stores it in PostgreSQL and applies detection rules
5. A React dashboard polls the API and displays alerts + telemetry in real-time

**Why it matters:** Understanding how endpoint monitoring works and what data to collect, how to detect anomalies, how to centralize visibility is core blue team work.

---

## Architecture

### High Level Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ AGENT (Python, Linux-only)                                  │
│ ├─ Collects system metrics (CPU, memory, disk %)            │
│ ├─ Parses running processes from `ps aux`                  │
│ ├─ Parses open ports from `netstat`                        │
│ ├─ Computes SHA256 hashes of monitored files               │
│ └─ Scrapes failed login count from `/var/log/auth.log`     │
└──────────────────┬──────────────────────────────────────────┘
                   │ POST /telemetry (JSON, every 5 sec)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ FASTAPI BACKEND (Python, Port 8000)                         │
│ ├─ Validates incoming JSON (Pydantic models)               │
│ ├─ Stores hosts, telemetry snapshots, processes, ports     │
│ ├─ Applies detection rules:                                 │
│ │  - File hash changes → FILE_MODIFIED alert               │
│ │  - CPU > 90% → CPU_HIGH alert                            │
│ │  - Memory > 90% → MEMORY_HIGH alert                      │
│ ├─ Exposes REST API (/telemetry, /alerts, /processes, etc)│
│ └─ Generates JWT tokens for auth (basic)                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ SQL queries
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ POSTGRESQL DATABASE (Port 5432)                             │
│ ├─ hosts: hostname, IP, last_seen                          │
│ ├─ telemetry: host_id, cpu_percent, memory_percent, etc    │
│ ├─ processes: host_id, pid, name, cpu%, memory%            │
│ ├─ ports: host_id, port, state (LISTEN/ESTABLISHED)       │
│ ├─ file_hashes: host_id, filepath, hash                    │
│ └─ alerts: host_id, alert_type, severity, details          │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP GET requests
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ REACT DASHBOARD (Port 3000)                                 │
│ ├─ Polls API every 2-5 seconds                             │
│ ├─ Displays telemetry panels (CPU, memory, disk charts)    │
│ ├─ Displays alerts with color-coding (red=critical, etc)   │
│ ├─ Shows process list with resource usage                  │
│ ├─ Shows open ports and their states                       │
│ └─ Shows monitored file hashes                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Agent (agent.py)

**What it collects, exactly:**

```python
{
  "hostname": "kripesh-IdeaPad",
  "timestamp": "2026-06-20T16:34:22Z",
  "cpu_percent": 12.5,           # Overall CPU usage
  "memory_percent": 48.3,         # RAM usage
  "disk_percent": 16.1,           # Root filesystem usage
  "processes": [
    {
      "pid": 1,
      "name": "systemd",
      "cpu_percent": 0,
      "memory_percent": 0.21
    },
    {
      "pid": 455,
      "name": "agent.py",
      "cpu_percent": 2.1,
      "memory_percent": 1.5
    }
  ],
  "ports": [
    {
      "port": 22,
      "state": "LISTEN"
    },
    {
      "port": 8000,
      "state": "LISTEN"
    }
  ],
  "file_hashes": {
    "/etc/passwd": "529d4776510d5ac8075640c8c41a19f29cabce0026268ae",
    "/etc/hosts": "39efcd28d49b93..."
  },
  "failed_logins": 0
}
```

**Collection interval:** Every 5 seconds (hardcoded, configurable in code)

**How it collects:**

| Data | Source | Method |
|------|--------|--------|
| CPU, memory, disk | `/proc/stat`, `psutil` | Read system files |
| Processes | `ps aux` output | Parse stdout |
| Open ports | `netstat -tuln` output | Parse stdout |
| File hashes | Direct file read | SHA256 hash |
| Failed logins | `/var/log/auth.log` | Grep for "Failed password" |

**Delivery:** HTTP POST to `http://backend:8000/telemetry` with JSON body. Expects 200 response.

---

### Backend (FastAPI)

**Receives JSON from agent → Validates → Stores → Detects anomalies**

#### Data Validation

Uses Pydantic models. Example:

```python
class Process(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

class TelemetryPayload(BaseModel):
    hostname: str
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    processes: List[Process]
    ports: List[Dict]
    file_hashes: Dict[str, str]
    failed_logins: int
```

Invalid JSON is rejected with 400 error.

#### Storage

On each telemetry POST:

1. **Lookup or create host record** in `hosts` table
2. **Store telemetry snapshot** in `telemetry` table
3. **Upsert process list** in `processes` table (pid + name + usage metrics)
4. **Upsert port list** in `ports` table
5. **Upsert file hashes** in `file_hashes` table
6. **Apply detection rules** → Create alerts in `alerts` table if triggered

#### Detection Rules (Hard-Coded Thresholds)

**File Modification Rule:**
- On each POST, compare incoming file hashes against **previous baseline** (last known hash for each file)
- If `hash["/etc/passwd"] != baseline["/etc/passwd"]` → Create `FILE_MODIFIED` alert with severity `critical`
- Details: `"/etc/passwd has changed from [old hash] to [new hash]"`

**CPU High:**
- If `cpu_percent > 90` → Create `CPU_HIGH` alert with severity `warning`
- Details: `"CPU usage high: 95.0%"`

**Memory High:**
- If `memory_percent > 90` → Create `MEMORY_HIGH` alert with severity `warning`

**Disk High:**
- If `disk_percent > 90` → Create `DISK_HIGH` alert with severity `critical`

**Brute Force (Failed Logins):**
- If `failed_logins > 5` within a rolling 60-second window → Create `BRUTE_FORCE_ATTEMPT` alert with severity `warning`
- Details: `"5+ failed SSH logins detected"`

#### API Endpoints

| Endpoint | Method | Returns |
|----------|--------|---------|
| `/telemetry` | POST | `{"status": "received"}` (stores data) |
| `/telemetry` | GET | Latest telemetry for all hosts |
| `/alerts` | GET | All alerts (newest first), paginated |
| `/processes` | GET | Process list for a specific host |
| `/ports` | GET | Port list for a specific host |
| `/file_hashes` | GET | File hashes for a specific host |
| `/hosts` | GET | List all monitored hosts |
| `/docs` | GET | Swagger UI (interactive API documentation) |

---

### Database (PostgreSQL)

**Complete schema:**

```sql
CREATE TABLE hosts (
  id SERIAL PRIMARY KEY,
  hostname VARCHAR(255) UNIQUE NOT NULL,
  ip_address VARCHAR(45),
  last_seen TIMESTAMP DEFAULT NOW()
);

CREATE TABLE telemetry (
  id SERIAL PRIMARY KEY,
  host_id INTEGER REFERENCES hosts(id),
  timestamp TIMESTAMP NOT NULL,
  cpu_percent FLOAT,
  memory_percent FLOAT,
  disk_percent FLOAT,
  processes_count INTEGER
);

CREATE TABLE processes (
  id SERIAL PRIMARY KEY,
  host_id INTEGER REFERENCES hosts(id),
  timestamp TIMESTAMP NOT NULL,
  pid INTEGER,
  name VARCHAR(255),
  cpu_percent FLOAT,
  memory_percent FLOAT
);

CREATE TABLE ports (
  id SERIAL PRIMARY KEY,
  host_id INTEGER REFERENCES hosts(id),
  timestamp TIMESTAMP NOT NULL,
  port INTEGER,
  state VARCHAR(50),
  service VARCHAR(255)
);

CREATE TABLE file_hashes (
  id SERIAL PRIMARY KEY,
  host_id INTEGER REFERENCES hosts(id),
  timestamp TIMESTAMP NOT NULL,
  filepath VARCHAR(500),
  hash VARCHAR(64)
);

CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  host_id INTEGER REFERENCES hosts(id),
  timestamp TIMESTAMP NOT NULL,
  alert_type VARCHAR(50),
  details TEXT,
  severity VARCHAR(20)
);
```


---

### Dashboard (React)

**Renders:**

1. **Telemetry Panel** — Shows latest CPU, memory, disk for each host
2. **Alerts Panel** — Lists alerts; color-coded by severity
3. **Processes Panel** — Top resource-consuming processes
4. **Ports Panel** — Active listening and established connections
5. **File Hashes Panel** — Monitored files and their current hashes

**Update mechanism:** Polling. Every 2-5 seconds, dashboard calls `GET /alerts`, `GET /telemetry`, etc. and re-renders.

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Agent telemetry collection | ✅ Full | CPU, memory, disk, processes, ports, file hashes, failed logins all working |
| Agent → Backend transmission | ✅ Full | HTTP POST with JSON; error handling included |
| Backend data validation | ✅ Full | Pydantic models reject invalid input |
| Backend data storage | ✅ Full | All data persisted to PostgreSQL |
| File modification detection | ✅ Full | Compares hashes, creates alerts, tested |
| Resource anomaly detection | ✅ Full | CPU/memory/disk thresholds; tested |
| Failed login detection | ✅ Full | Parses auth.log, counts; tested |
| Alert generation | ✅ Full | Alerts stored in DB with severity levels |
| Dashboard display | ✅ Full | All panels render; real data shown in screenshots |
| API endpoints | ✅ Full | All endpoints implemented; Swagger UI working |
| Docker Compose setup | ✅ Full | One-command deployment; all services containerized |
| Authentication | ⚠️ Partial | JWT tokens generated but not strictly enforced |
| Multi-host management | ⚠️ Partial | Schema supports it; tested with single agent |

---

## How to Run It

### Prerequisites

- **Docker & Docker Compose** (backend, database, frontend)
- **Python 3.9+** (agent, if running locally)
- **Linux/macOS** (agent uses `ps`, `netstat`, `/var/log/auth.log`)

### Quick Start

```bash
# Clone and navigate
git clone https://github.com/KripeshKhatiwada/EDR.git
cd EDR

# Start the full stack
docker-compose up --build
```

**Expected output (Terminal 1):**

```
backend-1     | INFO:     Uvicorn running on http://0.0.0.0:8000
backend-1     | INFO:     Application startup complete
frontend-1    | [vite] ... ready in 234ms
```

**In another terminal, run the agent:**

```bash
python agent.py
```

**Expected output (Terminal 2):**

```
[Agent] Collecting telemetry...
[Agent] POST /telemetry → 200 OK
[Agent] Data sent successfully
[Agent] Waiting 5 seconds...
[Agent] Collecting telemetry...
...
```

### Access Points

- **Dashboard:** http://localhost:3000 (React app)
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Database:** `postgresql://postgres:postgres@localhost:5432/edr_lite

---

## Real-World Workflow

### Step 1: Start the stack and agent

```bash
# Terminal 1
docker-compose up --build

# Terminal 2 (after backend starts)
python agent.py
```

### Step 2: Open the dashboard

Navigate to http://localhost:3000. You should see:
- Real-time CPU, memory, disk metrics
- Process list with resource usage
- Open ports
- Empty alerts panel (no anomalies yet)

### Step 3: Trigger a file modification alert

```bash
# In a third terminal, modify a monitored file
sudo touch /etc/passwd
```

**Result:** Within 5-10 seconds, the dashboard shows a new `FILE_MODIFIED` alert (red, critical).

### Step 4: Trigger a resource anomaly alert

```bash
# Spike CPU usage
stress --cpu 1 --timeout 30s
# (install with: apt install stress)
```

**Result:** Within 5-10 seconds, `CPU_HIGH` alert appears in the dashboard.

### Step 5: Verify in the database

```bash
# Check stored telemetry
docker exec edr-postgres-1 psql -U postgres -d edr -c "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5;"
```

**Expected output:**

```
id | host_id | timestamp | alert_type | details | severity
---|---------|-----------|------------|---------|----------
1  | 1       | 2026-06-20 16:34:22 | FILE_MODIFIED | /etc/passwd changed | critical
2  | 1       | 2026-06-20 16:34:35 | CPU_HIGH | CPU: 95.3% | warning
```

---

## Screenshots

### Screenshot 1: API Backend Running + Agent Collecting

![API Running](screenshots/api_running.png)

Left: FastAPI backend running on port 8000, ready to receive telemetry.
Right: Agent successfully sending telemetry every 5 seconds with "Data sent successfully" confirmation.

### Screenshot 2: Docker Compose Full Stack

![Docker Running](screenshots/docker_running.png)

All three services running: backend, frontend (Nginx), PostgreSQL. Ready for dashboard access.

### Screenshot 3: Dashboard Main View

![EDR Dashboard](screenshots/react_app_UI.png)

Central dashboard showing:
- **Telemetry panel** (left): Real-time CPU, memory, disk for each monitored host
- **Alerts panel** (center): Security alerts with color-coding
- **Ports panel** (bottom-left): Listening ports and their PIDs
- **Processes panel** (right): Running processes with CPU/memory
- **File Hashes panel** (bottom): Monitored files and their SHA256 hashes

### Screenshot 4: File Modification Alert

![File Modified Alert](screenshots/file_modified_alert.png)

Dashboard showing an active FILE_MODIFIED alert. When `/etc/passwd` hash changed, the system generated an alert with severity "critical" and timestamp.

### Screenshot 5: Telemetry Table

![Telemetry Table](screenshots/telemetry_table.png)

Raw telemetry data from the database. Each row is a snapshot from one collection cycle: hostname, CPU%, memory%, disk%, timestamp.

### Screenshot 6: Process Monitoring

![Process Table](screenshots/process_table.png)

Process list with resource usage: PID, process name, CPU%, memory%. Shows that the agent itself is running and consuming system resources.

### Screenshot 7: Alerts Log

![Alerts Table](screenshots/alerts_table.png)

Alert history. Each row is a triggered alert with type, severity, details, and timestamp. Shows the system successfully detecting anomalies.

---

## Configuration

### Agent

Edit `agent.py`:

```python
TARGET_URL = "http://localhost:8000"  # Backend URL
COLLECTION_INTERVAL = 5               # Seconds between collections
MONITORED_FILES = [
    "/etc/passwd",
    "/etc/hosts",
    "/etc/shadow"
]
```

### Backend

Edit `backend/main.py`:

```python
CPU_THRESHOLD = 90      # Percentage
MEMORY_THRESHOLD = 90   # Percentage
DISK_THRESHOLD = 90     # Percentage
FAILED_LOGIN_THRESHOLD = 5   # Count
FAILED_LOGIN_WINDOW = 60     # Seconds
```

### Database

Edit `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: edr
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
```

---

## What You Can Actually Use This For

1. **Learning:**
   - How real EDR systems collect and store endpoint data
   - How to build a detection pipeline (collect → analyze → alert)
   - Full-stack architecture (agent, API, database, dashboard)
   - Docker containerization and orchestration

2. **Portfolio:**
   - Shows you can ship a complete system (not just a script)
   - Demonstrates understanding of security monitoring concepts
   - Proves you can work across frontend, backend, database, infrastructure

3. **Interview Prep:**
   - Talk through how you'd scale to 10,000 endpoints (WebSocket updates, agent service, distributed storage)
   - Explain your detection logic and why you chose those thresholds
   - Discuss limitations and how you'd fix them in a production system

---

## Known Limitations

- **Polling, not real-time:** Dashboard updates every 2-5 seconds, not instant
- **Agent is manual:** Must run `python agent.py` each time; no systemd service
- **Single-host tested:** Schema supports multiple hosts; not extensively tested at scale
- **No encryption:** HTTP only; no TLS between agent and backend
- **Basic auth:** JWT tokens generated but not strictly validated on every request
- **No alert cleanup:** Database grows indefinitely; no archival policy
- **Linux only:** Agent uses `ps`, `netstat`, `/var/log/auth.log`
- **Basic detection:** Threshold-based rules only; no machine learning or statistical anomaly detection
- **No response automation:** Alerts are informational only; no auto-remediation

---

## Links

- **GitHub:** https://github.com/KripeshKhatiwada/EDR
- **Dashboard (running locally):** http://localhost:3000
- **API Docs (running locally):** http://localhost:8000/docs
- **Portfolio:** kripeshkhatiwada.github.io/portfolio-kripesh
