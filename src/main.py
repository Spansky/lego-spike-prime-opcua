import opcuaserver
from station import station
import signal 
import logging
import asyncio

def shutdown(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

async def main():
    await asyncio.gather(
        opcuaserver.run(),
        station.run_indicate_force()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
