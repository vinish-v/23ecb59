import time
from fastapi import APIRouter, HTTPException, status
from app.schemas.scheduler_schema import ScheduleRequest, ScheduleResponse, VehicleTask
from app.services.scheduler_service import SchedulerService
from app.utils.logger import log_info, log_error

router = APIRouter(prefix="/schedule", tags=["Scheduling Controller"])

@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
def run_scheduler(request: ScheduleRequest):
    """
    POST route triggering scheduling calculation for the given depot ID.
    Fetches details dynamically from the target API server.
    """
    start_time = time.time()
    log_info("controller", f"Received scheduling command for depot: {request.depotId}")
    
    try:
        # Retrieve the daily maintenance hour budget for the given depot
        budget = SchedulerService.get_depot_budget(request.depotId)
        
        # Retrieve tasks/vehicles from external endpoint
        vehicle_list = SchedulerService.get_vehicles()
        
        # Calculate optimal configuration of maintenance jobs
        tasks, duration, impact = SchedulerService.optimize_schedule(vehicle_list, budget)
        
        response = ScheduleResponse(
            depot_id=request.depotId,
            mechanic_hours_budget=budget,
            total_duration_spent=duration,
            total_impact_score=impact,
            selected_tasks=[
                VehicleTask(
                    TaskID=t["TaskID"],
                    Duration=t["Duration"],
                    Impact=t["Impact"]
                ) for t in tasks
            ]
        )
        
        elapsed = (time.time() - start_time) * 1000
        log_info("controller", f"Successfully completed schedule compilation. Duration: {elapsed:.1f}ms")
        return response
        
    except Exception as ex:
        log_error("controller", f"Failure during run_scheduler: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )
