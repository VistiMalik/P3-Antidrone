import utils.modes as modes
import utils.motorUtils as motorUtils
import website
import threading
import asyncio

# Global event to control the turret loop safely
stop_turret_event = threading.Event()

def run_turret():
    try:
        modes.setSetupMode()
        # Loop runs only while the turret event is NOT set
        while not stop_turret_event.is_set():
            modes.setIdleMode()
    except Exception as e:
        print(f"An error occurred in turret operation: {e}")

async def main():
    try:
        # Start turret
        turret_thread = threading.Thread(target=run_turret, daemon=True)
        turret_thread.start()
        
        # Start website
        flask_thread = threading.Thread(target=website.start_webpage, daemon=True)
        flask_thread.start()

        await website.start_socket()

    except KeyboardInterrupt:   # Handle Ctrl+C and other errors gracefully - puts turret back in home position
       print("Program terminated by user.")
    except Exception as e:
       print(f"An unexpected error occurred: {e}")
    finally:
        print("Stopping turret operation.")
        stop_turret_event.set()
        if 'turret_thread' in locals() and turret_thread.is_alive():
            turret_thread.join(timeout=2.0)

        print("Resetting motor position to home and closing website.")
        motorUtils.resetPosition()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Catch any final interrupts during shutdown
        pass

