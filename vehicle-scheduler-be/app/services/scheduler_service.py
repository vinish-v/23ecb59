import requests
from typing import List, Dict, Any, Tuple
from app.config import DEPOTS_API_URL, VEHICLES_API_URL, ACCESS_TOKEN
from app.utils.logger import log_info, log_error, log_warn

class SchedulerService:

    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    @classmethod
    def get_depot_budget(cls, depot_id: int) -> int:
        """
        Queries test API server to determine the mechanic-hour limit for a given depot.
        """
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
                    log_info("service", f"Depot {depot_id} limit resolved: {limit} hours.")
                    return limit
            
            log_warn("service", f"Depot ID {depot_id} is missing in response list.")
            raise Exception(f"Depot with ID {depot_id} is not configured on the remote server.")
        except Exception as e:
            log_error("service", f"Error resolving depot budget: {e}")
            raise

    @classmethod
    def get_vehicles(cls) -> List[Dict[str, Any]]:
        """
        Queries vehicles list needing operations maintenance.
        """
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
        """
        Solves the 0/1 Knapsack problem to find the optimal combination of vehicle maintenance
        tasks that maximizes the total operational impact score without exceeding the daily mechanic-hour budget.

        Parameters:
            vehicles (List[Dict]): List of dictionary items representing vehicles (with TaskID, Duration, Impact).
            budget (int): Daily limit of mechanic-hours (knapsack capacity).

        Returns:
            Tuple: (selected_vehicles_list, total_duration_spent, total_impact_score)
        """
        n = len(vehicles)
        if n == 0 or budget <= 0:
            return [], 0, 0
            
        # Step 1: Initialize the 2D DP Table (matrix of size [N + 1] x [Budget + 1])
        # dp[i][w] will store the maximum operational impact score achievable
        # using the first 'i' vehicles with a budget limit of 'w' hours.
        dp = [[0] * (budget + 1) for _ in range(n + 1)]
        
        # Step 2: Build the DP table bottom-up
        for i in range(1, n + 1):
            duration = vehicles[i - 1]["Duration"]  # Time cost of the task (weight)
            impact = vehicles[i - 1]["Impact"]      # Operational importance score (value)
            
            for w in range(budget + 1):
                # If the vehicle's duration is within the current budget limit 'w'
                if duration <= w:
                    # We have two choices:
                    # Choice A: Exclude the vehicle (keep previous max impact with same budget: dp[i-1][w])
                    # Choice B: Include the vehicle (get its impact + max impact of remaining budget: dp[i-1][w - duration] + impact)
                    # We pick the choice that yields the higher operational impact score.
                    dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - duration] + impact)
                else:
                    # If the vehicle's duration exceeds the current budget limit 'w', we cannot include it.
                    # We must exclude it and carry forward the previous maximum.
                    dp[i][w] = dp[i - 1][w]
                    
        # Step 3: Backtrack through the DP table to determine which vehicles were selected
        selected_tasks = []
        w = budget
        duration_total = 0
        
        for i in range(n, 0, -1):
            # If the value in dp[i][w] is different from the row above dp[i-1][w],
            # it means we decided to include the i-th vehicle to achieve that maximum impact score.
            if dp[i][w] != dp[i - 1][w]:
                vehicle = vehicles[i - 1]
                selected_tasks.append(vehicle)
                duration_total += vehicle["Duration"]  # Accumulate the selected duration
                w -= vehicle["Duration"]               # Reduce the remaining budget
                
        # Since we backtracked from the last item to the first, reverse the list
        # to match the order in which they appear in the original list.
        selected_tasks.reverse()
        total_impact = dp[n][budget]
        
        return selected_tasks, duration_total, total_impact
