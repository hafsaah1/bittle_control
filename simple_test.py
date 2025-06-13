# simple_test.py (Test 2: DSR/DTR)
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP'
BAUD_RATE = 115200

print("--- Final Test 2: Hardware Flow Control (DSR/DTR) ---")

try:
    print(f"Attempting to connect with dsrdtr=True...")
    
    # ==========================================================
    # v v v TESTING WITH DSR/DTR FLOW CONTROL v v v
    bittle_serial = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        timeout=2,
        dsrdtr=True  # <-- THE OTHER NEW SETTING
    )
    # ==========================================================
    # conenct to shape : 
    print("SUCCESS: Connected.")
    time.sleep(2)

    command_to_send = b'kcrF\n' # Using newline as the default terminator
    print(f"SENDING command: {command_to_send.decode().strip()}")
    bittle_serial.write(command_to_send)
    print("Command sent. Watch Bittle for 5 seconds.")
    time.sleep(5)

    print("SENDING command: d (Rest)")
    bittle_serial.write(b'd\n')
    time.sleep(1)

    bittle_serial.close()
    print("SUCCESS: Test finished.")

except Exception as e:
    print(f"\n!!! TEST FAILED. Error: {e}")