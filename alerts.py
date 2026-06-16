def check_alerts(data):
    alerts = []

    # CPU rule
    if data.cpu_percent > 80:
        alerts.append({
            "type": "CPU_HIGH",
            "message": f"CPU usage high: {data.cpu_percent}%",
            "severity": "warning"
        })

    # Memory rule
    if data.memory_percent > 85:
        alerts.append({
            "type": "MEMORY_HIGH",
            "message": f"Memory usage high: {data.memory_percent}%",
            "severity": "warning"
        })

    # Disk rule
    if data.disk_percent > 90:
        alerts.append({
            "type": "DISK_HIGH",
            "message": f"Disk usage high: {data.disk_percent}%",
            "severity": "critical"
        })

    return alerts