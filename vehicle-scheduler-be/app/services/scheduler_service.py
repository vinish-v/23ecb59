import requests
from typing import List, Dict, Any, Tuple
from ..config import DEPOTS_API_URL, VEHICLES_API_URL, ACCESS_TOKEN
from ..utils.logger import log_info, log_error, log_warn

class SchedulerService:

    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    @classmethod
    def get_depot_budget(cls, depot_id: int) -> int:
        log_info("service", f"Querying budget constraint for depot {depot_id}")
        headers = cls.get_headers()
        try:
            response = requests.get(DEPOTS_API_URL, headers=headers)
            if response.status_code != 200:
                log_error("service", f"Failed fetching depot limits. HTTP {response.status_code}")
                raise Exception("Unable to fetch data from test server API.")

            payload = response.json()
            depots = payload.get("depots", [])
            for depot in depots:
                if depot.get("ID") == depot_id:
                    limit = depot.get("MechanicHours")
                    if limit is None:
                        raise ValueError(f"Depot {depot_id} exists but has no MechanicHours field in API response.")
                    log_info("service", f"Depot {depot_id} limit resolved: {limit} hours.")
                    return int(limit)

            log_warn("service", f"Depot ID {depot_id} is missing in response list.")
            raise Exception(f"Depot with ID {depot_id} is not configured on the remote server.")
        except Exception as e:
            log_error("service", f"Error resolving depot budget: {e}")
            raise

    @classmethod
    def get_vehicles(cls) -> List[Dict[str, Any]]:
        log_info("service", "Retrieving vehicles maintenance requests dataset.")
        headers = cls.get_headers()
        try:
            response = requests.get(VEHICLES_API_URL, headers=headers)
            if response.status_code != 200:
                log_error("service", f"Failed fetching vehicles list. HTTP {response.status_code}")
                raise Exception("Unable to retrieve vehicles list from test server API.")

            payload = response.json()
            vehicles = payload.get("vehicles", [])
            log_info("service", f"Loaded {len(vehicles)} vehicle entries.")
            return vehicles
        except Exception as e:
            log_error("service", f"Error retrieving vehicles dataset: {e}")
            raise

    @staticmethod
    def optimize_schedule(vehicles: List[Dict[str, Any]], budget: int) -> Tuple[List[Dict[str, Any]], int, int]:
        n = len(vehicles)
        if budget is None:
            raise TypeError("budget must be an integer, got None.")
        if n == 0 or budget <= 0:
            return [], 0, 0

        dp = [[0] * (budget + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            duration = vehicles[i - 1]["Duration"]
            impact = vehicles[i - 1]["Impact"]
            for w in range(budget + 1):
                if duration <= w:
                    dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - duration] + impact)
                else:
                    dp[i][w] = dp[i - 1][w]

        selected_tasks = []
        w = budget
        duration_total = 0

        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                vehicle = vehicles[i - 1]
                selected_tasks.append(vehicle)
                duration_total += vehicle["Duration"]
                w -= vehicle["Duration"]

        selected_tasks.reverse()
        total_impact = dp[n][budget]

        return selected_tasks, duration_total, total_impact
