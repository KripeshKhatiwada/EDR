from fastapi import FastAPI
from pydantic import BaseModel
from database import Base , engine, SessionLocal
from models import TelemetryDB

app = FastAPI()

class Telemetry(BaseModel):
    hostname: str
    cpu_percent: float
    memory_percent: float        # data model how it should look like when we receive it from agent
    disk_percent: float
    
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "EDR-Lite backend running"}

@app.post("/telemetry")
def receive_telemetry(data: Telemetry):
    print("🔥 GOT REQUEST:", data)
    db=SessionLocal()  # create a new database session
    telemetry_data = TelemetryDB(
        hostname=data.hostname,
        cpu_percent=data.cpu_percent,
        memory_percent=data.memory_percent,
        disk_percent=data.disk_percent
    )
    db.add(telemetry_data)
    db.commit()
    db.close()
    return {"message": "data received and saved"}   # endpoint of this and check if it is working fine

@app.get("/telemetry")
def get_telemetry():
    db = SessionLocal()

    records = db.query(TelemetryDB).all()

    result = []

    for record in records:
        result.append({
            "id": record.id,
            "hostname": record.hostname,
            "cpu_percent": record.cpu_percent,
            "memory_percent": record.memory_percent,
            "disk_percent": record.disk_percent
        })

    db.close()

    return result