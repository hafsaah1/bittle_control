# your_calibrated_triangle.py
# This script executes the exact sequence you discovered to draw a triangle.
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Command Definitions ---
WALK_FORWARD = b'kwkF\n'
TURN_LEFT = b'kvtL\n'
BALANCE = b'kbalance\n'
REST = b'd\n'

# --- YOUR DISCOVERED TRIANGLE PROGRAM ---
# This is the exact sequence you found using the live driver.
YOUR_TRIANGLE_SEQUENCE = [
    WALK_FORWARD,
    BALANCE,
    TURN_LEFT,
    BALANCE,
    WALK_FORWARD,
    BALANCE,
    TURN_LEFT,
    WALK_FORWARD,
    BALANCE,
]

def connect_to_bittle():
    """Tries to connect to the serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Successfully connected to Bittle on {SERIAL_PORT}")
        time.sleep(2)
        return ser
     # return the ser we got from the begining : 
    except serial.SerialException as e:
        print(f"Error: Could not connect to {SERIAL_PORT}. Details: {e}")
        return None

def main():
    print("--- Running Your Calibrated Triangle Program ---")
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    try:
        # Start the Bittle in a balanced state
        print("Bittle standing by...")
        bittle_serial.write(BALANCE)
        time.sleep(2)

        print(f"Executing your sequence ({len(YOUR_TRIANGLE_SEQUENCE)} steps)...")
        
        # Loop through each command in the sequence you created
        for i, command in enumerate(YOUR_TRIANGLE_SEQUENCE):
            print(f"--> Sending step {i+1}: {command.decode().strip()}")
            bittle_serial.write(command)
            # A short pause for each action to complete
            time.sleep(2.0)
            # 1.5 is too slow , and we should be doing it at all 

        
        print("\n--- Your Triangle is Complete! ---")
        
    finally:
        # End by making the Bittle rest
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(REST)
            bittle_serial.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()