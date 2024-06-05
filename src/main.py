import opcuaserver
import signal 
import logging
import asyncio

def shutdown(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, loop)
    try:
        loop.run_until_complete(opcuaserver.run())
    finally:
        loop.close()
