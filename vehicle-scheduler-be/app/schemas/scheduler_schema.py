from pydantic import BaseModel
from typing import List

class ScheduleRequest(BaseModel):
    depotId: int

class VehicleTask(BaseModel):
    TaskID: str
    Duration: int
    Impact: int

class ScheduleResponse(BaseModel):
    depot_id: int
    mechanic_hours_budget: int
    total_duration_spent: int
    total_impact_score: int
    selected_tasks: List[VehicleTask]
