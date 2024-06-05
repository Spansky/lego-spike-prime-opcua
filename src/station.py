import time
from buildhat import Matrix, ForceSensor, Motor

# Connecting to the Lego Sensors
matrix_d = Matrix('D')
force_a = ForceSensor('A')
motor_c = Motor('C')

# Store the initial force as it is set on OPCUA server startup
force_value = force_a.get_force()

# Return the force
def get_force():
    return force_a.get_force()

# Indicate force with the Light Matrix
def indicate_force():
    force_val = get_force()
    if force_val == 0:
            matrix_d.level(0)
    elif 0 < force_val < 100:
        matrix_d.level((force_val - 1) // 10)
    elif force_val == 100:
        color_lightmatrix(9)

# A kind of hello world start sequence of actions when OPCUA server is started
def start_sequence(color):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (color, 5))
            time.sleep(0.05)
    move_motor(90, 20)
    move_motor(0, 20)

# color a 3x3 lightmatrix in one color 
def color_lightmatrix(colorcode):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (colorcode, 9))

def move_motor(angle, speed): 
    motor_c.run_to_position(angle, speed)
