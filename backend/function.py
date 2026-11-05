from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime ,timedelta


DB_PATH = "laundry.db"
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
    if block:
        machines = machines.filter(Machines.block == block)
    if kind:
        machines = machines.filter(Machines.kind == kind)
    response = []
    for machine in machines:
        minutes_left = None
        if machine.in_service == 0:
            state = "out of order"
        else:
            run = session.query(Runs).filter(Runs.machine_id == machine.id,Runs.status == "running" ).first()
            if run is None:
                state = "free"
            elif run.ends_at > datetime.now():
                state = "running"
            else:
                state = "waiting for pickup"
        temp = {
            "id": machine.id,
            "name": machine.name,
            "block": machine.block,
            "kind": machine.kind,
            "state": state,
            "minutes_left": minutes_left
        }
        response.append(temp)
    session.close()
    return response


def add_machine(name, block, kind, cycle_minutes):
    session = Session(engine)
    machine = Machines(
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

def update_machine_service(machine_id, in_service:int):
    session = Session(engine)
    machine = session.get(Machines,machine_id)
    if machine is None:
        session.close()
        return None
    if in_service == 0:
        run = session.query(Runs).filter(Runs.machine_id == machine_id,Runs.status == "running",Runs.ends_at > datetime.now()).first()
        if run:
            session.close()
            return "Machine is currently running"
    machine.in_service = in_service
    session.commit()
    response = {
        "message": "Machine status updated",
        "id": machine.id,
        "in_service": machine.in_service
    }
    session.close()
    return response



def start_machine_by_id(machine_id, roll_no):
    session = Session(engine)
    start_now = datetime.now()
    cycle_minuts = timedelta(minuts=30)
    end = start_now + cycle_minuts
    machine = session.get(Machines,id)
    run = Runs(machine_id=machine_id,
               roll_no = roll_no,
               starts_at = start_now,
               ends_at = end,
               status = "Started at")
    session.add(run)
    session.commit()
    session.refresh(run)
    
    response = {
        
        "id":machine.id,
         " roll_no" : machine.roll_no,
         "starts_at" : machine.starts_at,
         "ends_at" : machine.ends_at,
        "status" : machine.status
    }
    session.close()
    return response



