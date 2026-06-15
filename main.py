from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime   # we can use this to add timestamp to the telemetry but not now 

app = FastAPI()

class Telemetry(BaseModel):
    hostname: str
    cpu_percent: float
    memory_percent: float        # data model how it should look like when we receive it from agent
    disk_percent: float
    
telemetry_store=[]  # in-memory store  temp

@app.get("/")
def root():
    return {"status": "EDR-Lite backend running"}

@app.post("/telemetry")
def receive_telemetry(data: Telemetry):
    print(data)
    telemetry_store.append(data.model_dump())
    return {"message": "data received and running"}   # endpoint of this and check if it is working fine 

@app.get("/telemetry")
def get_telemetry():
    return telemetry_store