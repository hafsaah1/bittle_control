# square_drawer.py
# A script to make the Bittle walk in a square pattern.
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Action Definitions ---
# MODIFIED: This is your new requested sequence with three turns.
SQUARE_SEQUENCE = [
    b'kwkF\n', b'kwkF\n',          # Two steps forward
    b'ktrL\n', b'ktrL\n', b'ktrL\n',  # Three turns left
    b'kwkF\n', b'kwkF\n',   b'kwkF\n',          # Two steps forward
    b'ktrL\n', b'ktrL\n', b'ktrL\n'   # Three turns left
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

        print(f"Executing your sequence ({len(SQUARE_SEQUENCE)} steps)...")
        
        # Loop through each command in our sequence
        for i, command in enumerate(SQUARE_SEQUENCE):
            print(f"--> Sending step {i+1}: {command.decode().strip()}")
            bittle_serial.write(command)
            # You can adjust this time to make the actions smoother
            time.sleep(2.0)
        
        print("\n--- Sequence Complete! ---")
        
    finally:
        # End by making the Bittle rest
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n') # Command Bittle to rest
            bittle_serial.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
