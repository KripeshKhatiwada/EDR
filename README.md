# EDR Monitoring System

A Python-based Endpoint Detection and Response (EDR) monitoring project that collects endpoint telemetry, stores data in PostgreSQL, monitors running processes, and generates alerts based on system activity.

## Features

- Collect CPU, memory, and disk metrics using `psutil`
- Send telemetry to a FastAPI backend
- Store telemetry in PostgreSQL
- Support multiple monitored hosts
- Collect and store running processes
- Generate alerts for high CPU, memory, and disk usage

## Architecture

```text
Agent
  ↓
FastAPI Backend
  ↓
PostgreSQL
  ↓
Alert Engine
```

## Alert Engine

The alert engine analyzes incoming telemetry and generates alerts when configured thresholds are exceeded.

Current alert rules:

- CPU > 80%
- Memory > 85%
- Disk > 90%

### Alert Example

![Alert Engine](screenshots/alerts_table.png)

The screenshot above shows alerts generated and stored in PostgreSQL after resource usage exceeded configured thresholds.

## Additional Screenshots

Additional project screenshots can be found in the `screenshots/` folder:

- Backend receiving telemetry
- Telemetry stored in PostgreSQL
- Process monitoring data
- Alert generation
