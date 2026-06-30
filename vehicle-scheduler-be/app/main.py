from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import scheduler
from .utils.logger import log_info

app = FastAPI(
    title="Depot Vehicle Scheduler Microservice",
    description="Calculates optimal vehicle maintenance schedules to maximize operational impact.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scheduler.router)

@app.on_event("startup")
def startup_message():
    log_info("config", "Listening on port 8000.")

@app.get("/health", tags=["System Status"])
def health_endpoint():
    return {"status": "online", "service": "vehicle-scheduler-backend"}
