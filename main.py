from fastapi import FastAPI , Depends
from pydantic import BaseModel
from database import Base , engine, SessionLocal
from models import TelemetryDB
from sqlalchemy.orm import Session

app = FastAPI()

class Telemetry(BaseModel):
    hostname: str
    cpu_percent: float
    memory_percent: float        # data model how it should look like when we receive it from agent
    disk_percent: float
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "EDR-Lite backend running"}

@app.post("/telemetry")
def receive_telemetry(data: Telemetry, db: Session = Depends(get_db)):
    print("🔥 GOT REQUEST:", data)
    telemetry_data = TelemetryDB(
        hostname=data.hostname,
        cpu_percent=data.cpu_percent,
        memory_percent=data.memory_percent,
        disk_percent=data.disk_percent
    )
    db.add(telemetry_data)
    db.commit()
    # db.close()  # No need to close the session when using Depends
    return {"message": "data received and saved"}   # endpoint of this and check if it is working fine

@app.get("/telemetry")
def get_telemetry(db: Session = Depends(get_db)):
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

  

    return result

@app.get("/hosts")
def get_hosts(db: Session = Depends(get_db)):
    hosts = (
        db.query(TelemetryDB.hostname)
        .distinct()
        .all()
    )

    return [host[0] for host in hosts]

@app.get("/hosts/{hostname}")
def get_host_telemetry(
    hostname: str,
    db: Session = Depends(get_db)
):
    data = (
        db.query(TelemetryDB)
        .filter(TelemetryDB.hostname == hostname)
        .all()
    )

    return data

