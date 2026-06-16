import psutil
import json            # probably will be used uhhh soon
import requests
import socket
import time


backend_url = "http://localhost:8000/telemetry"
#collect system data
def collect_processes():
    processes = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_percent": proc.memory_percent()
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes

def collect_telemetry():
     return  {
    "hostname": socket.gethostname(),
    "cpu_percent": psutil.cpu_percent(interval=None),
    "memory_percent": psutil.virtual_memory().percent,  
    "disk_percent": psutil.disk_usage('/').percent,
    #"cpu_percent": 95,  # Simulated high CPU usage for testing
    #"memory_percent": 90,  # Simulated memory usage
   # "disk_percent": 95,  # Simulated disk usage
    "processes": collect_processes()
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

