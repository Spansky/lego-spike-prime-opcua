import asyncio
import logging
import os
import time
from asyncua import Server, ua
from asyncua.common.methods import uamethod
from signal import pause
from buildhat import Matrix, ForceSensor, Motor

# Connecting to the Lego Sensors
matrix_d = Matrix('D')
force_a = ForceSensor('A')
motor_c = Motor('C')

# Store the initial force as it is set on OPCUA server startup
force_value = force_a.get_force()

# Settings that can be set with ENV vars
opcconfig = {
    "port": os.getenv("OPCUA_PORT", 4840),
    "protocol": os.getenv("OPCUA_PROTOCOL", "opc.tcp"),
    "endpoint": os.getenv("OPCUA_ENDPOINT", "freeopcua/server/"),
    "host": os.getenv("OPCUA_HOST", "0.0.0.0"),
    "namespace": os.getenv("OPCUA_NAMESPACE", "http://pi301-lego.fritz.box")
}

# A kind of hello world start sequence of actions when OPCUA server is started
def start_sequence(color):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (color, 5))
            time.sleep(0.05)
    motor_c.run_to_position(90, 20)
    motor_c.run_to_position(0, 20)

# Toggle the LED-Matrix when calling this OPCUA-Function
@uamethod
def color_lightmatrix(parent, colorcode):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (colorcode, 9))

# Move the axis of the engine to a certain degree
@uamethod
def move_motor(parent, angle, speed):
    motor_c.run_to_position(angle, speed)

# The main loop that runs and keeps the server running
async def main():
    _logger = logging.getLogger(__name__)
    server = Server()
    await server.init()
    server.set_endpoint(
        f"{opcconfig.get('protocol')}://"
        f"{opcconfig.get('host')}:"
        f"{opcconfig.get('port')}/"
        f"{opcconfig.get('endpoint')}"
    )

    idx = await server.register_namespace(opcconfig.get('namespace'))

    # A OPCUA tag that reflects the pressure put on the assembly station
    opc_obj = await server.nodes.objects.add_object(idx, "ForceSensor")
    force = await opc_obj.add_variable(idx, "force", force_value)

    # Linking of the predefined @uamethod 'color_lightmatrix'
    await server.nodes.objects.add_method(
        ua.NodeId("LightMatrix", idx),
        ua.QualifiedName("LightMatrix", idx),
        color_lightmatrix,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )

    # Linking of the predefined @uamethod 'move_motor'
    await server.nodes.objects.add_method(
        ua.NodeId("SetEngineAngle", idx),
        ua.QualifiedName("SetEngineAngle", idx),
        move_motor,
        [ua.VariantType.Int64, ua.VariantType.Int64],
        [ua.VariantType.Int64]
    )

    _logger.info("Started server!")
    start_sequence(color=6)

    # We need to update the OPCUA tags 
    # - propably there is a smoother way to do so
    async with server:
        while True:
            await asyncio.sleep(0.5)
            force_val = force_a.get_force()
            await force.write_value(force_val)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=True)
    pause()
