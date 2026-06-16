from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class TelemetryDB(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)


class ProcessDB(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String)
    pid = Column(Integer)
    process_name = Column(String)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)

class AlertDB(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String)
    alert_type = Column(String)
    message = Column(String)
    severity = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)