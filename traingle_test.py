# triangle_drawer.py
# A script to make Bittle draw a specific 70-40-70 degree triangle.
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Action Definitions ---
WALK_FORWARD = b'kwkF\n'
# Using the pivot turn for sharp corners!
TURN_LEFT = b'kvtL\n' 

# --- Sequence for your 70-40-70 Triangle ---
# We will walk Side A, turn at the 40-degree corner, walk Side B, etc.
TRIANGLE_SEQUENCE = [
    # Walk Side A (let's say 3 steps)
    WALK_FORWARD, WALK_FORWARD, WALK_FORWARD,
    # Turn at the 40-degree vertex (external angle = 140 deg). Let's try 3 turns.
    TURN_LEFT, TURN_LEFT, TURN_LEFT,
    
    # Walk Side B (should be same length as Side A)
    WALK_FORWARD, WALK_FORWARD, WALK_FORWARD,
    # Turn at the first 70-degree vertex (external angle = 110 deg). Let's try 2 turns.
    TURN_LEFT, TURN_LEFT,
    
    # Walk Side C (this side will be shorter)
    WALK_FORWARD, WALK_FORWARD,
    # Turn at the final 70-degree vertex to face the start direction.
    TURN_LEFT, TURN_LEFT
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
    print("--- Starting Bittle Custom Triangle Drawing Test ---")
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    try:
        # Start the Bittle in a balanced state
        print("Bittle standing by...")
        bittle_serial.write(b'kbalance\n')
        time.sleep(2)

        print(f"Executing Triangle sequence ({len(TRIANGLE_SEQUENCE)} steps)...")
        
        # Loop through each command in our sequence
        for i, command in enumerate(TRIANGLE_SEQUENCE):
            print(f"--> Sending step {i+1}: {command.decode().strip()}")
            bittle_serial.write(command)
            
            # Use different timings for walking vs. turning for better results
            if command == WALK_FORWARD:
                time.sleep(2.5) # A longer pause for walking
            else: # It's a turn command
                time.sleep(1.5) # A shorter pause for turning
        
        print("\n--- Triangle Complete! ---")
        
    finally:
        # End by making the Bittle rest
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n') # Command Bittle to rest
            bittle_serial.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
