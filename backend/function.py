from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta

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
    query = session.query(Machines)
    if block:
        query = query.filter(Machines.block(block))
    if kind:
        query = query.filter(Machines.kind(kind))
    machines = query.all()
    response = []
    for machine in machines:
        if machine.in_service == 0:
            state = "out of order"
        else:
            run = session.query(Runs).filter(Runs.machine_id == machine.id, Runs.status == "running").order_by(Runs.id.desc()).first()
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
            "state": state
        }
        response.append(temp)
    session.close()
    return response

def get_machine_by_id(machine_id):
    session = Session(engine)
    machine = session.get(Machines, machine_id)
    if machine is None:
        session.close()
        return None
    if machine.in_service == 0:
        state = "out of order"
    else:
        run = session.query(Runs).filter(Runs.machine_id == machine.id, Runs.status == "running").order_by(Runs.id.desc()).first()
        if run is None:
            state = "free"
        elif run.ends_at > datetime.now():
            state = "running"
        else:
            state = "waiting for pickup"
    runs = session.query(Runs).filter(Runs.machine_id == machine_id).order_by(Runs.id.desc()).limit(5).all()
    last_runs = []
    for run in runs:
        last_runs.append({
            "id": run.id,
            "roll_no": run.roll_no,
            "started_at": str(run.started_at) if run.started_at else None,
            "ends_at": str(run.ends_at) if run.ends_at else None,
            "collected_at": str(run.collected_at) if run.collected_at else None,
            "status": run.status
        })
    response = {
        "id": machine.id,
        "name": machine.name,
        "block": machine.block,
        "kind": machine.kind,
        "cycle_minutes": machine.cycle_minutes,
        "in_service": machine.in_service,
        "state": state,
        "runs": last_runs
    }
    session.close()
    return response

def add_machine(id, name, block, kind, cycle_minutes):
    session = Session(engine)
    if id:
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
    session.refresh(machine)
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

def update_machine_service(machine_id, in_service: int):
    session = Session(engine)
    machine = session.get(Machines, machine_id)
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
    machine = session.get(Machines, machine_id)
    if machine is None:
        session.close()
        return None
    if machine.in_service == 0:
        session.close()
        return "Machine is out of order"
    if not roll_no:
        session.close()
        return "Roll number is required"
    last_run = session.query(Runs).filter(Runs.machine_id == machine_id, Runs.status == "running").order_by(Runs.id.desc()).first()
    if last_run:
        session.close()
        return "Machine is currently in use"
    existing_student_run = session.query(Runs).filter(Runs.roll_no == roll_no, Runs.status == "running").first()
    if existing_student_run:
        session.close()
        return "Student already has an active run"
    start_now = datetime.now()
    minutes = machine.cycle_minutes 
    end = start_now + timedelta(minutes=minutes)
    run = Runs(
        machine_id=machine_id,
        roll_no=roll_no,
        started_at=start_now,
        ends_at=end,
        status="running"
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    response = {
        "id": run.id,
        "machine_id": machine.id,
        "roll_no": run.roll_no,
        "started_at": str(run.started_at),
        "ends_at": str(run.ends_at),
        "status": run.status
    }
    session.close()
    return response

def collect_run(run_id, roll_no):
    session = Session(engine)
    run = session.get(Runs, run_id)
    if run is None:
        run = session.query(Runs).filter(Runs.machine_id == run_id, Runs.status == "running").order_by(Runs.id.desc()).first()
    if run is None:
        session.close()
        return None
    if run.status != "running":
        session.close()
        return "Run is already collected or cleared"
    if run.roll_no != roll_no:
        session.close()
        return "Not allowed. Only the student who started this run can collect"
    if run.ends_at > datetime.now():
        session.close()
        return "Cycle has not finished yet"
    run.status = "collected"
    run.collected_at = datetime.now()
    session.commit()
    response = {
        "message": "Clothes collected",
        "id": run.id,
        "status": run.status,
        "collected_at": str(run.collected_at)
    }
    session.close()
    return response

def clear_machine(machine_id, roll_no):
    session = Session(engine)
    machine = session.get(Machines, machine_id)
    if machine is None:
        session.close()
        return None
    if not roll_no:
        session.close()
        return "Roll number is required"
    last_run = session.query(Runs).filter(Runs.machine_id == machine_id, Runs.status == "running").order_by(Runs.id.desc()).first()
    if not last_run:
        session.close()
        return "No active run for this machine"
    if last_run.ends_at > datetime.now():
        session.close()
        return "Cycle has not finished yet"
    last_run.status = "cleared"
    session.commit()
    response = {
        "id": last_run.id,
        "machine_id": last_run.machine_id,
        "roll_no": last_run.roll_no,
        "status": last_run.status
    }
    session.close()
    return response







    return response



