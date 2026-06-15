from sqlalchemy import Column, Integer, String, Float
from database import Base

class TelemetryDB(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)