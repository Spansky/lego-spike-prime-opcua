import time
import asyncio
from buildhat import Matrix, ForceSensor, Motor, Matrix

# Connecting to the Lego Sensors
led_matrix = Matrix('D')
force_sensor = ForceSensor('A')
motor = Motor('C')

# Store the initial force as it is set on OPCUA server startup
force_value = force_sensor.get_force()

# Return the force
def get_force():
    return force_sensor.get_force()

# Indicate force with the Light Matrix
def indicate_force():
    force_val = get_force()
    if force_val == 0:
        color_lightmatrix(3)
    elif 0 < force_val < 100:
        color_lightmatrix(8)
    elif force_val == 100:
        color_lightmatrix(9)

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

def indicate_force_level(percentage :int):
    color_neutral :str = ""
    color_meter :str = "green"
    first_digit :int = percentage // 10
    second_digit :int = percentage % 10

    col :int = first_digit % 3
    row :int = first_digit // 3 

    for fill_up_row in range(0,row):
        for col in range(0,3):
            led_matrix.set_pixel((2-fill_up_row, col), (color_meter, 10))

    for remaining_row in range(row, 3):
        for col in range(0,3):
            led_matrix.set_pixel((2-remaining_row, col), (color_neutral, 10))


    #    for column in range(0,3):
    #        print(f"row: {fill_up_row}, column: {column}")
    #        led_matrix.set_pixel((fill_up_row,column),
    #           (colorcode, 9))
#    for fill_up_col in range(0, col):
#        led_matrix.set_pixel((row + 1, fill_up_col), (colorcode, 9))
#
#    led_matrix.set_pixel((row + 1, col + 1),
#                         (colorcode,
#                         second_digit))

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

