import utils.setupMode as setupMode
import utils.idleMode as idleMode
import website
import threading
import asyncio

def run_turret():
    setupMode.setSetupMode()
    while True:
        idleMode.setIdleMode()

async def main():
    # Start turret
    turret_thread = threading.Thread(target=run_turret)
    turret_thread.start()
    
    flask_thread = threading.Thread(target=website.start_webpage, daemon=True)
    flask_thread.start()


    await website.start_socket()

if __name__ == "__main__":
    asyncio.run(main())