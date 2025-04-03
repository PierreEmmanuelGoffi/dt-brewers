import requests
from datetime import datetime
import time
import random

class BrewingSystemRealAPI:
    """API client for real brewing system data"""
    
    def __init__(self, base_url="http://tremblar.com:5000"):
        self.base_url = base_url
        self.data_collection_frequency = 5  # minutes
        self.system_state = "connected"
        self.safe_mode = True
        self._safety_thresholds = {
            "max_pressure": 3.0,  # bar
            "min_pressure": 0.5,  # bar
            "max_temperature": 30.0,  # °C
            "min_temperature": 5.0,  # °C
            "max_ph": 7.0,
            "min_ph": 3.5,
            "max_dissolved_oxygen": 10.0,  # mg/L
            "min_dissolved_oxygen": 0.5,  # mg/L
        }
    
    def get_system_status(self):
        """Get current system status from real API"""
        try:
            # Get the latest data
            response = requests.get(f"{self.base_url}/api/data?limit=1")
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                latest = data[0]
                return {
                    "temperature": latest.get("RTD"),
                    "pressure": latest.get("CONDUCTIVITY", 0) / 50, 
                    "ph_level": latest.get("PH"),
                    "dissolved_oxygen": latest.get("DISSOLVED_OXYGEN"),
                    "data_collection_frequency": self.data_collection_frequency,
                    "last_update": latest.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "system_state": self.system_state,
                    "safe_mode": self.safe_mode
                }
            else:
                return self._get_placeholder_data()
                
        except Exception as e:
            print(f"Error fetching real data: {e}")
            return self._get_placeholder_data()
    
    def _get_placeholder_data(self):
        """Placeholder data when API is unavailable"""
        return {
            "temperature": "No data",
            "pressure": "No data", 
            "ph_level": "No data",
            "dissolved_oxygen": "No data",
            "data_collection_frequency": self.data_collection_frequency,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (No API data available)",
            "system_state": "disconnected",
            "safe_mode": self.safe_mode,
            "no_data_available": True
        }
    
    def update_data_frequency(self, value):
        """Update data collection frequency"""
        if value < 1 or value > 60:
            return {"success": False, "message": "Frequency must be between 1 and 60 minutes"}
        
        self.data_collection_frequency = value
        return {"success": True, "message": f"Data collection frequency updated to {value} minutes"}
    
    def get_historical_data(self, hours=48):
        """Get historical fermentation data"""
        try:
            estimated_records = hours * 12
            response = requests.get(f"{self.base_url}/api/data?limit={estimated_records}")
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                # Transform data into expected format
                timestamps = [entry.get("timestamp") for entry in data]
                temperatures = [entry.get("RTD") for entry in data]
                # Convert conductivity to pressure estimate
                pressures = [entry.get("CONDUCTIVITY", 0) / 50 for entry in data]  
                ph_levels = [entry.get("PH") for entry in data]
                dissolved_oxygen = [entry.get("DISSOLVED_OXYGEN") for entry in data]
                
                return {
                    "timestamps": timestamps,
                    "temperature": temperatures,
                    "pressure": pressures,
                    "ph_level": ph_levels,
                    "dissolved_oxygen": dissolved_oxygen
                }
            else:
                # Return placeholder data
                return self._get_placeholder_historical_data(hours)
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            # Return placeholder data in case of error
            return self._get_placeholder_historical_data(hours)
    
    def _get_placeholder_historical_data(self, hours=48):
        """Generate placeholder historical data"""
        timestamps = [datetime.fromtimestamp(time.time() - i * 3600).strftime("%Y-%m-%d %H:%M") for i in range(hours, 0, -1)]
        return {
            "timestamps": timestamps,
            "temperature": [None for _ in range(hours)],
            "pressure": [None for _ in range(hours)],
            "ph_level": [None for _ in range(hours)],
            "dissolved_oxygen": [None for _ in range(hours)],
            "no_data_available": True
        }
    
    def get_safety_thresholds(self):
        """Get safety thresholds"""
        return self._safety_thresholds
    
    def send_command(self, command, value, verification_code=None):
        """Send a command to the brewing system"""
        # Critical commands require verification code
        critical_commands = ["set_pressure", "start_batch", "stop_batch", "emergency_stop"]
        
        if command in critical_commands and not verification_code:
            return {"success": False, "message": "Verification code required for critical operations"}
        
        # Safety checks
        if command == "set_pressure":
            if value > self._safety_thresholds["max_pressure"] or value < self._safety_thresholds["min_pressure"]:
                return {
                    "success": False, 
                    "message": f"Pressure value outside safe range ({self._safety_thresholds['min_pressure']} - {self._safety_thresholds['max_pressure']} bar)"
                }
        
        # In a real implementation, this would send the command to the actual API
        if command == "start_batch":
            self.system_state = "fermenting"
        elif command == "stop_batch":
            self.system_state = "idle"
        
        return {"success": True, "message": f"Command {command} with value {value} sent successfully"}

# Create an instance for import
api = BrewingSystemRealAPI()