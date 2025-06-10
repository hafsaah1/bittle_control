# simple_test.py
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP'
BAUD_RATE = 115200

print("--- Starting Bittle Minimum Connection Test ---")

try:
    # Step 1: Connect to the Bittle
    print(f"Attempting to connect to Bittle on {SERIAL_PORT}...")
    bittle_serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print("SUCCESS: Connected to Bittle.")
    # Wait for the connection to fully establish
    time.sleep(2)

    # Step 2: Send a single, simple movement command
    command_to_send = b'kcrF\n'  # Command to Crawl Forward
    print(f"SENDING command: {command_to_send.decode().strip()} (Crawl Forward)")
    bittle_serial.write(command_to_send)
    print("Command sent. Bittle should be crawling forward now for 5 seconds.")

    # Step 3: Wait for 5 seconds to observe the Bittle
    time.sleep(5)

    # Step 4: Send the "Rest" command to stop it
    print("SENDING command: d (Rest)")
    bittle_serial.write(b'd\n')
    print("Rest command sent.")
    time.sleep(1)

    # Step 5: Close the connection
    bittle_serial.close()
    print("SUCCESS: Connection closed. Test finished.")

except serial.SerialException as e:
    print(f"\n!!! TEST FAILED: Could not connect to {SERIAL_PORT}.")
    print("Please check that Bittle is on and connected in your computer's Bluetooth settings.")
    print(f"Error details: {e}")

except Exception as e:
    print(f"\n!!! An unexpected error occurred: {e}")