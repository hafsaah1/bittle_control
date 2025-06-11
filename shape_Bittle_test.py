# square_drawer.py
# A script to make the Bittle walk in a square pattern.
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Action Definitions ---
# This is our program for drawing a square.
# We will repeat the "walk forward, turn 90 degrees" action 4 times.
# Based on your calibration, we'll try using 2 'ktrL' commands for a 90-degree turn.
SQUARE_SEQUENCE = [
    b'kwkF\n', b'ktrL\n', b'ktrL\n',  # Side 1 & Corner 1
    b'kwkF\n', b'ktrL\n', b'ktrL\n',  # Side 2 & Corner 2
    b'kwkF\n', b'ktrL\n', b'ktrL\n',  # Side 3 & Corner 3
    b'kwkF\n', b'ktrL\n', b'ktrL\n'   # Side 4 & Corner 4
]

def connect_to_bittle():
    """Tries to connect to the serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Successfully connected to Bittle on {SERIAL_PORT}")
        time.sleep(2)
        return ser
    except serial.SerialException as e:
        print(f"Error: Could not connect to {SERIAL_PORT}. Details: {e}")
        return None

def main():
    print("--- Starting Bittle Square Drawing Test ---")
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    try:
        # Start the Bittle in a balanced state
        print("Bittle standing by...")
        bittle_serial.write(b'kbalance\n')
        time.sleep(2)

        print(f"Executing square sequence ({len(SQUARE_SEQUENCE)} steps)...")
        
        # Loop through each command in our sequence
        for i, command in enumerate(SQUARE_SEQUENCE):
            print(f"--> Sending step {i+1}: {command.decode().strip()}")
            bittle_serial.write(command)
            # You can adjust this time to make the actions smoother
            time.sleep(2.0)
        
        print("\n--- Square Complete! ---")
        
    finally:
        # End by making the Bittle rest
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n') # Command Bittle to rest
            bittle_serial.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
