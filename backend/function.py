from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime ,timedelta


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




def get_all_machines(block=None, kind=None):
    session = Session(engine)
    machines = session.query(Machines)
    response = []
    for machine in machines:
    
        if machine.in_service == 0:
            state = "out of order"
        else:
            run = session.query(Runs).filter(Runs.machine_id == machine.id,Runs.status == "running" ).first()
            if run.ends_at > datetime.now():
             state = "running"        
            else:
             state = "waiting for pickup"
        temp = {
            "id": machine.id,
            "name": machine.name,
            "block": machine.block,
            "kind": machine.kind,
            "state": state
            
       
        }
        
        if block:
            print(Machines.block)
        if kind:
            print(Machines.kind)
    response.append(temp)
    session.commit()
    session.close()
    return response



def add_machine(id, name, block, kind, cycle_minutes):
    session = Session(engine)
    machine = Machines(
        id=id,
        name=name,
        block=block,
        kind=kind,
        cycle_minutes=cycle_minutes,
        in_service=1
    )
    session.add(machine)
    session.commit()
    response = {
        "id": machine.id,
        "name": machine.name,
        "block": machine.block,
        "kind": machine.kind,
        "cycle_minutes": machine.cycle_minutes,
        "in_service": machine.in_service
    }
    session.close()
    return response
