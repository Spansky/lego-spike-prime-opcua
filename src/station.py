import time
import asyncio
from buildhat import Matrix, ForceSensor, Motor, Matrix

# Connecting to the Lego Sensors
led_matrix = Matrix('D')
force_sensor = ForceSensor('A')
motor = Motor('C')

# parametrizable station params
force_sweet_spot = 8 

# Return the force
def get_force():
    return force_sensor.get_force()

# A kind of hello world start sequence of actions when OPCUA server is started
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

def indicate_sweet_spot(force_sweet_spot):
    color_sweet_spot = "blue"
    row = 2 - (force_sweet_spot // 3)
    col = force_sweet_spot % 3
    led_matrix.set_pixel((row,col),(color_sweet_spot, 9))

def indicate_force_level(percentage :int):
    if not (0 <= percentage <= 100):
        raise ValueError("Percentage must be between 0 and 100.")

    color_neutral :str = ""
    color_meter :str = "green"

    filled_cells = int(percentage / 10)

    for i in range(9):
        row = 2 - (i // 3) # reversed row index
        col = i % 3
        if i < filled_cells:
            led_matrix.set_pixel((row, col),(color_meter, 10))
        elif i == filled_cells and percentage % 10 != 0:
            led_matrix.set_pixel((row, col),(color_meter, percentage % 10))
        else:
            led_matrix.set_pixel((row, col),(color_neutral, 0))

def move_motor(angle, speed): 
    motor.run_to_position(angle, speed)

# Infinite loop to continuously indicate force
async def run_indicate_force():
    try:
        while True:
            indicate_force_level(get_force())
            await asyncio.sleep(0.05)  # Delay to control the loop speed
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

