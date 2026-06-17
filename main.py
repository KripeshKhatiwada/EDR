from fastapi import FastAPI , Depends
from pydantic import BaseModel
from database import Base , engine, SessionLocal
from models import FailedLoginDB, PortDB, TelemetryDB, ProcessDB, AlertDB, FileHashDB
from sqlalchemy.orm import Session
from alerts import check_alerts

app = FastAPI()

class Process(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

class Port(BaseModel):
    pid: int | None = None
    port: int


class Telemetry(BaseModel):
    hostname: str
    cpu_percent: float
    memory_percent: float        # data model how it should look like when we receive it from agent
    disk_percent: float
    processes: list[Process]
    ports: list[Port]
    file_hashes: dict = {}      # placeholder for file hashes, can be expanded to a list of dicts if we want more details
    failed_logins: int

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

### This is the main endpoint where we receive telemetry data from the agent. It saves the data to the database and runs the alert engine and further added things if i do.

def receive_telemetry(data: Telemetry, db: Session = Depends(get_db)):
    print(
    f"🔥 GOT REQUEST from {data.hostname} "
    f"CPU={data.cpu_percent}% "
    f"RAM={data.memory_percent}% "
    f"DISK={data.disk_percent}% "
    f"Processes={len(data.processes)} "
    f"Ports={len(data.ports)}"
    f"Failed Logins={data.failed_logins}"
        )
    telemetry_data = TelemetryDB(
        hostname=data.hostname,
        cpu_percent=data.cpu_percent,
        memory_percent=data.memory_percent,
        disk_percent=data.disk_percent
    )
    db.add(telemetry_data)
    db.commit()
    db.refresh(telemetry_data)



    failed_login_data = FailedLoginDB(
        hostname=data.hostname,
        count=data.failed_logins
    )
    db.add(failed_login_data)
    db.commit()
    db.refresh(failed_login_data)



    for process in data.processes:
        try:
            process_row = ProcessDB(
                hostname=data.hostname,
                pid=process.pid,
                process_name=process.name or "Unknown",
                cpu_percent=process.cpu_percent or 0.0,
                memory_percent=process.memory_percent or 0.0
            )
            db.add(process_row)
        except Exception as e:
            print(f"Error processing process data: {e}")
            continue
    db.commit()


    for port in data.ports:
        try:
            port_row = PortDB(
                hostname=data.hostname,
                pid=port.pid,
                port=port.port
            )
            db.add(port_row)
        except Exception as e:
            print(f"Error processing port data: {e}")
            continue
        

    for filepath, new_hash in data.file_hashes.items():

        existing = (
            db.query(FileHashDB)
            .filter(
                FileHashDB.hostname == data.hostname,
                FileHashDB.file_path == filepath
            )
            .first()
        )

        if existing:

            if existing.hash_value != new_hash:

                alert_row = AlertDB(
                    hostname=data.hostname,
                    alert_type="FILE_MODIFIED",
                    message=f"{filepath} was modified",
                    severity="critical"
                )

                db.add(alert_row)

                existing.hash_value = new_hash

                print(f"🚨 FILE MODIFIED: {filepath}")

        else:

            file_row = FileHashDB(
                hostname=data.hostname,
                file_path=filepath,
                hash_value=new_hash
            )

            db.add(file_row)
    db.commit()

    alerts = check_alerts(data)   # running alert engine

    for alert in alerts:
        alert_row = AlertDB(
            hostname=data.hostname,
            alert_type=alert["type"],    #save any alerts
            message=alert["message"],
            severity=alert["severity"]
        )
        db.add(alert_row)
        print("🚨 ALERT TRIGGERED:", alert["message"])

    db.commit()
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

@app.get("/processes")
def get_processes(db: Session = Depends(get_db)):
    records = db.query(ProcessDB).all()

    return [
        {
            "id": r.id,
            "hostname": r.hostname,
            "pid": r.pid,
            "process_name": r.process_name,
            "cpu_percent": r.cpu_percent,
            "memory_percent": r.memory_percent
        }
        for r in records
    ]

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    records = db.query(AlertDB).all()

    return [
        {
            "id": r.id,
            "hostname": r.hostname,
            "alert_type": r.alert_type,
            "message": r.message,
            "severity": r.severity,
            "created_at": r.created_at
        }
        for r in records
    ]

@app.get("/ports")
def get_ports(db: Session = Depends(get_db)):
    records = db.query(PortDB).all()

    return [
        {
            "id": r.id,
            "hostname": r.hostname,
            "pid": r.pid,
            "port": r.port
        }
        for r in records
    ]


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

