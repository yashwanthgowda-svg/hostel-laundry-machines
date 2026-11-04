from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime


DB_PATH = "./laundry.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


class Machines(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    kind = Column(String)
    block = Column(String)
    cycle_minutes = Column(Integer)
    in_service = Column(Integer)


class Runs(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    roll_no = Column(String)
    started_at = Column(DateTime, default=datetime.now)
    ends_at = Column(DateTime)
    collected_at = Column(DateTime, nullable=True)
    status = Column(String)


Base.metadata.create_all(engine)
