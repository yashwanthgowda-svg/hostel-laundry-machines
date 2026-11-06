from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import function
app = FastAPI()
from function import Session, engine, Machines


@app.on_event("startup")
def add_sample_machines():

    session = Session(engine)

    count = session.query(Machines).count()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Machine(BaseModel):
    id: int
    name: str
    block: str
    kind: str
    cycle_minutes: int


@app.get("/machines")
def get_all_machines(block: str = None, kind: str = None):
    result = function.get_all_machines(
        block=block,
        kind=kind
    )
    return result


@app.get("/machines/{machine_id}")
def get_machine_by_id(machine_id: int):
    result = function.get_machine_by_id(machine_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Machine doesn't exist"
        )
    return result


@app.post("/machines")
def add_machine(machine: Machine):
    result = function.add_machine(
        machine.id,
        machine.name,
        machine.block,
        machine.kind,
        machine.cycle_minutes
    )
    return result


@app.patch("/service/{machine_id}")
def update_machine_service(machine_id: int, in_service: int):
    result = function.update_machine_service(
        machine_id,
        in_service
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Machine doesn't exist"
        )
    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result
        )
    return result


@app.post("/runs/{machine_id}")
def start_machine(machine_id: int, roll_no: str):
    result = function.start_machine_by_id(
        machine_id,
        roll_no
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Machine doesn't exist"
        )
    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result
        )
    return result


@app.patch("/collect/{run_id}")
def collect_run(run_id: int, roll_no: str):
    result = function.collect_run(
        run_id,
        roll_no
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Run doesn't exist"
        )
    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result
        )
    return result


@app.patch("/clear/{machine_id}")
def clear_machine(machine_id: int, roll_no: str):
    result = function.clear_machine(
        machine_id,
        roll_no
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Machine doesn't exist"
        )
    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result
        )
    return result







