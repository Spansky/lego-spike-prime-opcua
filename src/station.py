import time
import asyncio
from buildhat import Matrix, ForceSensor, Motor, Matrix, Hat

# Showing some status information in stdout
print("Station is starting...")
hat = Hat()
print(f"Connected devices: {hat.get()}")


# Connecting to the Lego Sensors
led_matrix = Matrix('D')
force_sensor = ForceSensor('A')
motor = Motor('C')

# parametrizable station params
force_upper_limit = 99
station_status = "Idle"
station_result = "OK" # "NOK"

# Return the force
def get_force():
    return force_sensor.get_force()

def get_force_upper_limit():
    return force_upper_limit

def get_station_status():
    return station_status

def get_station_result():
    return station_result

def set_force_upper_limit(limit: int):
    if not (0 <= limit <= 100):
        raise ValueError("Force upper limit must be between 0 and 9.")
    force_upper_limit = limit

# A kind of hello world start sequence
def start_sequence(color):
    for r in range(0,3):
        for c in range(0,3):
            led_matrix.set_pixel((r,c), (color, 5))
            time.sleep(0.05)
    move_motor(90, 20)
    move_motor(0, 20)

# Color a 3x3 light matrix in one color 
def color_lightmatrix(colorcode):
    for r in range(0,3):
        for c in range(0,3):
            led_matrix.set_pixel((r,c), (colorcode, 9))

def indicate_force_level(percentage :int):
    if not (0 <= percentage <= 100):
        raise ValueError("Percentage must be between 0 and 100.")


    color_neutral :str = ""
    color_meter :str = "green"

    filled_cells = int(percentage / 10)
    limit_cell = min(int(force_upper_limit / 10), 8)

    if percentage > force_upper_limit:
        color_meter = "red"
        station_result = "NOK"
    else:
        color_meter = "green"
        station_result = "OK"
    for i in range(9):
        row = 2 - (i // 3) # reversed row index
        col = i % 3
        if i < filled_cells:
            led_matrix.set_pixel((row, col),(color_meter, 10))
        elif i == filled_cells and percentage % 10 != 0:
            led_matrix.set_pixel((row, col),(color_meter, percentage % 10))
        else:
            led_matrix.set_pixel((row, col),(color_neutral, 0))

    # Set the limit cell
    limit_row = 2 - (limit_cell // 3)
    limit_col = limit_cell % 3
    if percentage <= force_upper_limit:
        led_matrix.set_pixel((limit_row, limit_col),("yellow", 10))

def move_motor(angle, speed): 
    motor.run_to_position(angle, speed)

# Infinite loop to continuously indicate force
async def run_indicate_force():
    try:
        while True:
            indicate_force_level(get_force())
            await asyncio.sleep(0.1)  # Delay to control the loop speed
    except asyncio.CancelledError:
        print("Force indication stopped.")

# Main function to run tasks concurrently
async def main():
    await asyncio.ensure_future(
        run_indicate_force()
    )

# Start the endless force indication process and OPCUA server
if __name__ == "__main__":
    start_sequence(6)
    asyncio.run(main())

