import asyncio
import logging
import os
import time
import station

from asyncua import Server, ua
from asyncua.common.methods import uamethod

# Settings that can be set with ENV vars
opcconfig = {
    "port": os.getenv("OPCUA_PORT", 4840),
    "protocol": os.getenv("OPCUA_PROTOCOL", "opc.tcp"),
    "endpoint": os.getenv("OPCUA_ENDPOINT", "freeopcua/server/"),
    "host": os.getenv("OPCUA_HOST", "0.0.0.0"),
    "namespace": os.getenv("OPCUA_NAMESPACE", "http://pi301-lego.fritz.box")
}

# Toggle the LED-Matrix when calling this OPCUA-Function
@uamethod
def color_lightmatrix(parent, colorcode):
    station.color_lightmatrix(colorcode)

# Move the axis of the engine to a certain degree
@uamethod
def move_motor(parent, angle, speed):
    station.move_motor(angle, speed)

# The main loop that runs and keeps the server running
async def run():
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
    force = await opc_obj.add_variable(idx, "force", station.get_force())

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
    station.start_sequence(color=6)

    # We need to update the OPCUA tags 
    async with server:
        while True:
            await asyncio.sleep(0.1)
            await force.write_value(station.get_force())

if __name__ == "__main__":
    asyncio.run(run())


