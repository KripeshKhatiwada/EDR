import psutil
import json
import requests
import socket
import time


backend_url = "http://localhost:8000/telemetry"
#collect system data

def collect_telemetry():
     return  {
    "hostname": socket.gethostname(),
    "cpu_percent": psutil.cpu_percent(interval=1),
    "memory_percent": psutil.virtual_memory().percent,  
    "disk_percent": psutil.disk_usage('/').percent,
}

#send data to backend
def send_telemetry(data):
    try:
        response = requests.post(backend_url, json=data)
        if response.status_code in [200, 201]:
            print("Data sent successfully")
        else:
            print(f"Failed to send data: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
        while True:
            data = collect_telemetry()
            send_telemetry(data)
            time.sleep(10)  # send data every 10 seconds

