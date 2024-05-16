import asyncio
import logging
import os
import time
from asyncua import Server, ua
from asyncua.common.methods import uamethod
from signal import pause
from buildhat import Matrix, ForceSensor, Motor
matrix_d = Matrix('D')
force_a = ForceSensor('A')
motor_c = Motor('C')

force_value = force_a.get_force()

opcconfig = {
    "port": os.getenv("OPCUA_PORT", 4840),
    "protocol": os.getenv("OPCUA_PROTOCOL", "opc.tcp"),
    "endpoint": os.getenv("OPCUA_ENDPOINT", "freeopcua/server/"),
    "host": os.getenv("OPCUA_HOST", "0.0.0.0"),
    "namespace": os.getenv("OPCUA_NAMESPACE", "http://pi301-lego.fritz.box")
}

restconfig = {
    "port": os.getenv("REST_PORT", 8000),
    "host": os.getenv("REST_HOST", "0.0.0.0"),
}

def start_sequence(color):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (color, 5))
            time.sleep(0.05)
    motor_c.run_to_position(90, 20)
    motor_c.run_to_position(0, 20)

@uamethod
def color_lightmatrix(parent, colorcode):
    for r in range(0,3):
        for c in range(0,3):
            matrix_d.set_pixel((r,c), (colorcode, 9))

@uamethod
def move_motor(parent, angle, speed):
    motor_c.run_to_position(angle, speed)

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

    opc_obj = await server.nodes.objects.add_object(idx, "ForceSensor")
    force = await opc_obj.add_variable(idx, "force", force_value)

    await server.nodes.objects.add_method(
        ua.NodeId("LightMatrix", idx),
        ua.QualifiedName("LightMatrix", idx),
        color_lightmatrix,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )

    await server.nodes.objects.add_method(
        ua.NodeId("SetEngineAngle", idx),
        ua.QualifiedName("SetEngineAngle", idx),
        move_motor,
        [ua.VariantType.Int64, ua.VariantType.Int64],
        [ua.VariantType.Int64]
    )

    _logger.info("Starting server!")
    start_sequence(color=6)
    async with server:
        while True:
            await asyncio.sleep(0.5)
            force_val = force_a.get_force()
            await force.write_value(force_val)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=True)
    pause()
