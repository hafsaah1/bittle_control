# calibrated_shape_drawer.py
# A script to draw precise shapes using calibrated turn data.
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Calibrated Action Definitions ---
# From your testing, we now know these are the basic building blocks for our shapes.
WALK_FORWARD = b'kwkF\n'
# You discovered that 2 pivot turns make a 90-degree corner!
TURN_90_DEGREES = [b'kvtL\n', b'kvtL\n']

# --- Shape Sequences ---
# We build our shapes using the calibrated actions above.

# 1. The Square Sequence (4 sides, 4 corners of 90 degrees)
SQUARE_SEQUENCE = []
for _ in range(4): # Repeat 4 times for 4 sides
    SQUARE_SEQUENCE.append(WALK_FORWARD)
    SQUARE_SEQUENCE.extend(TURN_90_DEGREES) # Add the two-turn sequence for the corner

# 2. The Custom Triangle Sequence (70-40-70)
# Calculation: If 2 turns = 90 deg, then 1 turn = 45 deg.
# - Turn at 40-deg corner (140 deg external) = 140/45 = ~3 turns
# - Turn at 70-deg corner (110 deg external) = 110/45 = ~2 turns
TURN_140_DEGREES = [b'kvtL\n'] * 3
TURN_110_DEGREES = [b'kvtL\n'] * 2

TRIANGLE_SEQUENCE = [
    WALK_FORWARD, # Side A
    *TURN_140_DEGREES, # Turn at 40-degree corner
    WALK_FORWARD, # Side B
    *TURN_110_DEGREES, # Turn at 70-degree corner
    WALK_FORWARD, # Side C
    *TURN_110_DEGREES  # Final turn at 70-degree corner
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
    print("--- Starting Calibrated Shape Drawer ---")
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    # ==========================================================
    # CHOOSE WHICH SHAPE TO DRAW HERE
    # ==========================================================
    # By default, we will draw the SQUARE.
    sequence_to_run = SQUARE_SEQUENCE
    shape_name = "SQUARE"
    
    # To draw the triangle, comment out the two lines above and uncomment the two below:
    # sequence_to_run = TRIANGLE_SEQUENCE
    # shape_name = "TRIANGLE"
    # ==========================================================

    try:
        print("Bittle standing by...")
        bittle_serial.write(b'kbalance\n')
        time.sleep(2)

        print(f"Executing {shape_name} sequence ({len(sequence_to_run)} steps)...")
        
        for i, command in enumerate(sequence_to_run):
            print(f"--> Sending step {i+1}: {command.decode().strip()}")
            bittle_serial.write(command)
            
            if command == WALK_FORWARD:
                time.sleep(2.5)
            else: # It's a turn command
                time.sleep(1.5)
        
        print(f"\n--- {shape_name} Complete! ---")
        
    finally:
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n')
            bittle_serial.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
