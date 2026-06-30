import time
from fastapi import APIRouter, HTTPException, status
from ..schemas.scheduler_schema import ScheduleRequest, ScheduleResponse, VehicleTask
from ..services.scheduler_service import SchedulerService
from ..utils.logger import log_info, log_error

router = APIRouter(prefix="/schedule", tags=["Scheduling Controller"])

@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
def run_scheduler(request: ScheduleRequest):

    start_time = time.time()
    log_info("controller", f"Received scheduling command for depot: {request.depotId}")
    
    try:
        budget = SchedulerService.get_depot_budget(request.depotId)
        if budget is None:
            raise ValueError(f"Depot {request.depotId} has no MechanicHours configured on the remote server.")
            
        vehicle_list = SchedulerService.get_vehicles()
        tasks, duration, impact = SchedulerService.optimize_schedule(vehicle_list, budget)
        
        response = ScheduleResponse(
            depot_id=request.depotId,
            mechanic_hours_budget=budget,
            total_duration_spent=duration,
            total_impact_score=impact,
            selected_tasks=[
                VehicleTask(
                    TaskID=str(t.get("TaskID", "")),
                    Duration=int(t.get("Duration", 0)),
                    Impact=int(t.get("Impact", 0))
                ) for t in tasks
            ]
        )
        
        elapsed = (time.time() - start_time) * 1000
        log_info("controller", f"Succes Duration: {elapsed:.1f}ms")
        return response
        
    except Exception as ex:
        log_error("controller", f"Failure during run_scheduler: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )
