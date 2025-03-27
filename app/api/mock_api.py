import random
from datetime import datetime

class BrewingSystemAPI:
    """Mock API for the brewing system digital twin"""
    
    def __init__(self):
        self.data_collection_frequency = 5  # minutes
        self.safe_mode = True
        self.system_state = "idle"
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
        """Get current system status"""
        return {
            "temperature": round(random.uniform(20.0, 25.0), 1),
            "pressure": round(random.uniform(1.0, 2.5), 2),
            "ph_level": round(random.uniform(4.5, 5.5), 1),
            "dissolved_oxygen": round(random.uniform(2.0, 8.0), 2),
            "data_collection_frequency": self.data_collection_frequency,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_state": self.system_state,
            "safe_mode": self.safe_mode
        }
    
    def update_data_frequency(self, value):
        """Update data collection frequency"""
        if value < 1 or value > 60:
            return {"success": False, "message": "Frequency must be between 1 and 60 minutes"}
        
        self.data_collection_frequency = value
        return {"success": True, "message": f"Data collection frequency updated to {value} minutes"}
    
    def get_historical_data(self, hours=48):
        """Get historical fermentation data"""
        import time
        
        timestamps = [time.time() - i * 3600 for i in range(hours, 0, -1)]
        return {
            "timestamps": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") for ts in timestamps],
            "temperature": [round(random.uniform(20.0, 25.0), 1) for _ in timestamps],
            "pressure": [round(random.uniform(1.0, 2.5), 2) for _ in timestamps],
            "ph_level": [round(random.uniform(4.5, 5.5), 1) for _ in timestamps],
            "dissolved_oxygen": [round(random.uniform(2.0, 8.0), 2) for _ in timestamps]
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
        
        # Mock successful command
        if command == "start_batch":
            self.system_state = "fermenting"
        elif command == "stop_batch":
            self.system_state = "idle"
        
        return {"success": True, "message": f"Command {command} with value {value} sent successfully"}

# Create an instance for import
api = BrewingSystemAPI()