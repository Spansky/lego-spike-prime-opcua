import time
import asyncio
from buildhat import Matrix, ForceSensor, Motor, Matrix, Hat

class Station:
    def __init__(self, force_upper_limit: int):
        self.force_upper_limit = force_upper_limit
        self.station_status = "Idle"
        self.station_result = "OK" # "NOK"

        self.sensors = {
            "force_sensor": ForceSensor('A'),
            "led_matrix": Matrix('D'),
            "motor": Motor('C')
        }

    def get_force(self):
        return self.sensors.get('force_sensor').get_force()
    
    def get_force_upper_limit(self):
        return self.force_upper_limit
    
    def get_station_status(self):
        return self.station_status
    
    def get_station_result(self):
        return self.station_result
    
    def set_force_upper_limit(self, limit: int):
        if not (0 <= limit <= 100):
            raise ValueError("Force upper limit must be between 0 and 9.")
        self.force_upper_limit = limit
        print("Adjusted force upper limit to: ", self.force_upper_limit)

    def reset_station_result(self):
        self.station_result = "OK"
    
    # A kind of hello world start sequence
    def start_sequence(self,color):
        for r in range(0,3):
            for c in range(0,3):
                self.sensors.get('led_matrix').set_pixel((r,c), (color, 5))
                time.sleep(0.05)
        self.move_motor(90, 20)
        self.move_motor(0, 20)
    
    # Color a 3x3 light matrix in one color 
    def color_lightmatrix(self, colorcode):
        for r in range(0,3):
            for c in range(0,3):
                self.sensors.get('led_matrix').set_pixel((r,c), (colorcode, 9))
    
    def indicate_force_level(self, percentage :int):
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100.")
    
        color_neutral :str = ""
        color_meter :str = "green"
    
        filled_cells = int(percentage / 10)
        limit_cell = min(int(self.force_upper_limit / 10), 8)
    
        if percentage > self.force_upper_limit:
            color_meter = "red"
            self.station_result = "NOK"
        else:
            color_meter = "green"
        for i in range(9):
            row = 2 - (i // 3) # reversed row index
            col = i % 3
            if i < filled_cells:
                self.sensors.get('led_matrix').set_pixel((row, col),(color_meter, 10))
            elif i == filled_cells and percentage % 10 != 0:
                self.sensors.get('led_matrix').set_pixel((row, col),(color_meter, percentage % 10))
            else:
                self.sensors.get('led_matrix').set_pixel((row, col),(color_neutral, 0))
    
        # Set the limit cell
        limit_row = 2 - (limit_cell // 3)
        limit_col = limit_cell % 3
        if percentage <= self.force_upper_limit:
            self.sensors.get('led_matrix').set_pixel((limit_row, limit_col),("yellow", 10))
    
    def move_motor(self, angle, speed): 
        self.sensors.get('motor').run_to_position(angle, speed)
    
    # Infinite loop to continuously indicate force
    async def run_indicate_force(self):
        try:
            while True:
                self.indicate_force_level(self.get_force())
                await asyncio.sleep(0.1)  # Delay to control the loop speed
        except asyncio.CancelledError:
            print("Force indication stopped.")
 
station = Station(99)
# Main function to run tasks concurrently
async def main():
    await asyncio.ensure_future(
        station.run_indicate_force()
    )

# Start the endless force indication process and OPCUA server
if __name__ == "__main__":
    station.start_sequence(6)
    asyncio.run(main())

