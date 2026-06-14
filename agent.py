import psutil
import json

data = {
    "cpu": psutil.cpu_percent(interval=1),
    "memory": psutil.virtual_memory().percent,
    "disk": psutil.disk_usage('/').percent,
}

print(json.dumps(data, indent=4))