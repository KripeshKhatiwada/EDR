def check_alerts(data):
    alerts = []

    suspicious_ports = [4444, 5555, 1337]

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

    # Suspicious ports
    for port in data.ports:
        if port.port in suspicious_ports:
            alerts.append({
                "type": "SUSPICIOUS_PORT",
                "message": f"Suspicious port detected: {port.port}",
                "severity": "critical"
            })

    # Failed logins
    if data.failed_logins > 10:
        alerts.append({
            "type": "FAILED_LOGINS",
            "message": f"{data.failed_logins} failed login attempts",
            "severity": "warning"
        })

    return alerts