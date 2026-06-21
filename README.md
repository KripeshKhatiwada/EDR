# 🛡️ EDR Lite – Endpoint Detection & Response System

A **full-stack Endpoint Detection & Response (EDR)** system that collects endpoint telemetry in real-time, detects security anomalies, and visualizes system activity through a centralized web dashboard.

Built with **Python (FastAPI)**, **React**, **PostgreSQL**, and **Docker**.

---

## 🎯 Overview

EDR Lite is a learning/portfolio project that simulates a real-world security monitoring pipeline. An agent runs on monitored hosts, collecting system metrics and security events. The backend ingests, stores, and analyzes this data. The dashboard provides real-time visibility into endpoint activity.

**This is not production-grade software.** See [Limitations](#limitations) below.

---

## 🚀 Key Features

### 📡 Real-Time Telemetry Collection
- **System Metrics**: CPU, memory, disk usage (captured every 5 seconds)
- **Process Monitoring**: Running processes with PID, name, CPU%, memory%
- **Port Monitoring**: Listening and established connections
- **File Integrity Monitoring**: SHA256 hashes of critical system files
- **Security Events**: Failed login attempts from system logs

### 🔐 Security Detection
- **File Modification Detection** — Alerts when monitored file hashes change (e.g., `/etc/passwd`, `/etc/hosts`, critical binaries)
- **Resource Anomaly Detection** — Alerts on CPU/memory/disk spikes above configurable thresholds
- **Failed Login Tracking** — Detects brute-force attempts (5+ failed logins in 60 seconds)

### 📊 Centralized Dashboard
- Real-time telemetry visualization (CPU, memory, disk charts)
- Process list with resource consumption
- Active port monitoring
- File hash tracking
- Security alert log with severity levels
- Multi-host support

### 🐳 Full Docker Stack
- Containerized backend (FastAPI)
- Containerized frontend (React/Nginx)
- PostgreSQL database
- One-command deployment: `docker-compose up --build`

---

## 🏗️ Architecture

### Data Pipeline

```
Agent (runs on monitored host)
  ↓ (collects telemetry)
POST /telemetry (JSON payload)
  ↓
FastAPI Backend (validates, stores, analyzes)
  ↓ (stores in PostgreSQL)
PostgreSQL Database
  ↓
React Dashboard (polls /alerts, /telemetry, /processes)
  ↓
Browser (real-time display)
```

### Agent

**Runs as a Python script on monitored hosts.**

Collects every 5 seconds:
- CPU usage (overall %)
- Memory usage (% of total)
- Disk usage (% of total)
- Process list: `ps aux` parsed into {pid, name, cpu%, memory%}
- Open ports: `netstat` parsed into {port, state}
- File hashes: SHA256 of `/etc/passwd`, `/etc/hosts`, monitored binaries
- Failed logins: Parsed from `/var/log/auth.log` (failed SSH attempts)

Sends as JSON POST to `http://backend:8000/telemetry`:
```json
{
  "hostname": "kripesh-IdeaPad",
  "timestamp": "2026-06-20T16:34:22Z",
  "cpu_percent": 12.5,
  "memory_percent": 48.3,
  "disk_percent": 16.1,
  "processes": [
    {"pid": 1, "name": "systemd", "cpu_percent": 0, "memory_percent": 0.2},
    {"pid": 455, "name": "agent.py", "cpu_percent": 2.1, "memory_percent": 1.5}
  ],
  "ports": [
    {"port": 22, "state": "LISTEN"},
    {"port": 8000, "state": "LISTEN"}
  ],
  "file_hashes": {
    "/etc/passwd": "529d4776510d5ac8075640c8c41a19f29cabce0026...",
    "/etc/hosts": "39efcd28d49b93..."
  },
  "failed_logins": 0
}
```

### Backend (FastAPI)

**HTTP API that receives, validates, stores, and analyzes telemetry.**

#### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/telemetry` | POST | Receive agent telemetry (validated with Pydantic) |
| `/telemetry` | GET | Retrieve latest telemetry for all hosts |
| `/alerts` | GET | Retrieve triggered security alerts |
| `/processes` | GET | Retrieve process list for a host |
| `/ports` | GET | Retrieve open ports for a host |
| `/file_hashes` | GET | Retrieve monitored file hashes |
| `/hosts` | GET | List all monitored hosts |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

#### Detection Rules

**File Modification:**
- On each telemetry, compare incoming file hashes with baseline
- If hash mismatch: trigger `FILE_MODIFIED` alert with severity `critical`

**Resource Anomaly:**
- If `cpu_percent > 90%`: trigger `CPU_HIGH` alert with severity `warning`
- If `memory_percent > 90%`: trigger `MEMORY_HIGH` alert with severity `warning`
- If `disk_percent > 90%`: trigger `DISK_HIGH` alert with severity `critical`

**Brute Force:**
- If `failed_logins > 5` in last 60 seconds: trigger `BRUTE_FORCE_ATTEMPT` alert with severity `warning`

### Database (PostgreSQL)

**Stores all telemetry and alerts.**

#### Schema

```sql
hosts
  id (PK)
  hostname (UNIQUE)
  ip_address
  last_seen (timestamp)

telemetry
  id (PK)
  host_id (FK → hosts)
  timestamp
  cpu_percent
  memory_percent
  disk_percent
  processes_count

processes
  id (PK)
  host_id (FK → hosts)
  timestamp
  pid
  name
  cpu_percent
  memory_percent

ports
  id (PK)
  host_id (FK → hosts)
  timestamp
  port
  state (LISTEN | ESTABLISHED)
  service

file_hashes
  id (PK)
  host_id (FK → hosts)
  timestamp
  filepath
  hash (SHA256)

alerts
  id (PK)
  host_id (FK → hosts)
  timestamp
  alert_type (FILE_MODIFIED | CPU_HIGH | MEMORY_HIGH | DISK_HIGH | BRUTE_FORCE_ATTEMPT)
  details (human-readable description)
  severity (critical | warning | info)
```

### Dashboard (React)

**Web UI for security analysts to monitor endpoints.**

Real-time visualization:
- **Telemetry Panel**: Latest CPU, memory, disk for each host
- **Alerts Panel**: Security alerts with severity color-coding (red=critical, orange=warning)
- **Processes Panel**: Top resource-consuming processes
- **Ports Panel**: Listening and established connections
- **File Hashes Panel**: Monitored files and their hashes
- **Hosts Panel**: List of all monitored endpoints

Updates via polling (every 2-5 seconds):
```javascript
// Poll for alerts
GET /alerts → Update alerts panel

// Poll for telemetry
GET /telemetry → Update CPU/memory/disk charts

// Poll for processes
GET /processes → Update process list
```

---

## ⚙️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for running agent locally)
- Linux/macOS (agent collects from `ps`, `netstat`, `/var/log/auth.log`)

### Quick Start

```bash
git clone https://github.com/KripeshKhatiwada/EDR.git
cd EDR

# Start the full stack
docker-compose up --build

# In another terminal, run the agent
python agent.py
```

**What you should see:**

Terminal 1 (Docker):
```
backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8000
backend-1   | INFO:     Application startup complete
frontend-1  | [vite] ... ready in XXX ms
```

Terminal 2 (Agent):
```
[Agent] Collecting telemetry...
[Agent] POST /telemetry → 200 OK
[Agent] Data sent successfully
[Agent] Waiting 5 seconds...
```

### Access

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database**: `postgresql://postgres:postgres@localhost:5432/edr`

---

## 🖼️ Screenshots

### System Dashboard
![EDR Dashboard](screenshots/react_app_UI.png)
Central dashboard showing telemetry, alerts, processes, ports, and file hashes for all monitored hosts.

### Alert Detection in Action
![File Modified Alert](screenshots/file_modified_alert.png)
Real-time alert when a monitored file (`file_integrity_check.txt`) is modified. Dashboard shows alert type, details, and severity.

### Telemetry Data
![Telemetry Table](screenshots/telemetry_table.png)
System metrics collected from the monitored host (CPU, memory, disk usage over time).

### Process Monitoring
![Process Table](screenshots/process_table.png)
List of running processes with resource consumption (PID, process name, CPU%, memory%).

### Alerts Log
![Alerts Table](screenshots/alerts_table.png)
Security alert log with timestamps, types, and severity levels.

### Backend Telemetry Collection
![API Running](screenshots/api_running.png)
FastAPI backend receiving telemetry POST requests and agent sending data successfully.

### Full Stack Running
![Docker Running](screenshots/docker_running.png)
Docker Compose with all services running (backend, frontend, database).

---

## 🔧 Configuration

### Agent Configuration

Edit `agent.py`:

```python
TARGET_URL = "http://localhost:8000"  # Backend URL
COLLECTION_INTERVAL = 5  # Seconds between telemetry collections
MONITORED_FILES = [
    "/etc/passwd",
    "/etc/hosts",
    "/etc/shadow"
]
```

### Backend Configuration

Edit `backend/main.py`:

```python
# Detection thresholds
CPU_THRESHOLD = 90  # %
MEMORY_THRESHOLD = 90  # %
DISK_THRESHOLD = 90  # %
FAILED_LOGIN_THRESHOLD = 5  # Count
FAILED_LOGIN_WINDOW = 60  # Seconds
```

### Database Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: edr
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
```

---

## 🧪 Testing

### 1. Verify Telemetry Collection

```bash
# Check if data is flowing into the database
docker exec edr-postgres-1 psql -U postgres -d edr -c "SELECT * FROM telemetry LIMIT 5;"
```

Expected output:
```
 id |          hostname          | timestamp | cpu_percent | memory_percent
----+----------------------------+-----------+-------------+----------------
  1 | kripesh-IdeaPad-Slim-3-15  | 2026-06-20 | 12.5        | 48.3
  2 | kripesh-IdeaPad-Slim-3-15  | 2026-06-20 | 10.2        | 47.8
```

### 2. Test File Modification Alert

```bash
# Modify a monitored file
sudo touch /etc/hosts

# Check dashboard or API
curl http://localhost:8000/alerts

# Should see: FILE_MODIFIED alert with details about the changed file
```

### 3. Test Resource Spike Alert

```bash
# Spike CPU usage
stress --cpu 1 --timeout 30s  # (requires: apt install stress)

# Check dashboard
# Should see: CPU_HIGH alert when CPU exceeds 90%
```

### 4. Test Failed Login Alert

```bash
# Attempt SSH with wrong password (5+ times)
ssh invalid_user@localhost

# Check dashboard or API
curl http://localhost:8000/alerts | grep BRUTE_FORCE
```

---

## 📊 Example Workflow

1. **Start the stack**: `docker-compose up --build` (terminal 1)
2. **Start the agent**: `python agent.py` (terminal 2)
3. **Open dashboard**: http://localhost:3000
4. **Monitor in real-time**: CPU, memory, disk, processes update every 5 seconds
5. **Trigger an alert**: Modify `/etc/passwd` or spike CPU
6. **See alert immediately**: Dashboard shows new security alert with severity
7. **Investigate**: Click on alert to see details, check affected host, review process list

---

## ⚠️ Limitations

**This is a learning project, not production software.**

- **No real-time updates** — Dashboard uses polling, not WebSockets. 2-5 second delay vs. true real-time.
- **Agent requires manual execution** — No persistent background agent or systemd service yet.
- **Basic detection rules** — Threshold-based only, no ML/anomaly detection. Easy to evade with slow attacks.
- **No persistence rotation** — Alert log grows indefinitely; no cleanup or archival.
- **Minimal authentication** — Basic JWT token validation, no RBAC or advanced access control.
- **Single-agent testing only** — Multi-agent management not fully tested.
- **Linux-only agent** — Collects from `/var/log/auth.log`, `ps`, `netstat` (Linux tools).
- **No encryption in transit** — HTTP only, no TLS/SSL yet.

---

## 🚀 Future Improvements

- Real-time WebSocket updates for instant alert notifications
- Background agent service (systemd or Docker-based persistent agent)
- Advanced anomaly detection (statistical, behavioral, ML-based)
- Role-based access control (RBAC) for multi-user dashboards
- Cloud deployment (AWS/GCP/Azure infrastructure)
- Alert response automation (auto-isolate hosts, kill processes, etc.)
- Multi-platform agent (Windows, macOS support)
- TLS/encrypted communication between agent and backend
- Alert archival and log rotation
- Integration with SIEM platforms (Elasticsearch, Splunk)

---

## 🏆 What This Demonstrates

This project shows:
- **Full-stack development**: Backend (Python/FastAPI), frontend (React), database (PostgreSQL)
- **Real-world security concepts**: Telemetry collection, anomaly detection, alerting
- **Systems programming**: Process monitoring, network introspection, file hashing
- **DevOps**: Docker containerization, multi-service orchestration
- **API design**: RESTful endpoints, data validation (Pydantic), structured responses
- **Database design**: Relational schema for time-series security data

---

## 📝 Author

**Kripesh Khatiwada**  
Cybersecurity Student | Blue Team | Endpoint Detection Systems

---

## 📄 License

MIT License (or your choice of license)

---

## 🔗 Links

- **GitHub**: https://github.com/KripeshKhatiwada/EDR
- **Dashboard**: http://localhost:3000 (when running)
- **API Docs**: http://localhost:8000/docs (when running)