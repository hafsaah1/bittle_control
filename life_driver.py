# live_driver.py
# A script to control the Bittle live with keyboard presses to build shapes.
import cv2
import serial
import time
import numpy as np # <--- THIS IS THE MISSING LINE THAT FIXES THE ERROR

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Command Definitions ---
WALK_FORWARD = b'kwkF\n'
TURN_LEFT = b'kvtL\n'
TURN_RIGHT = b'kvtR\n'
BALANCE = b'kbalance\n'
REST = b'd\n'

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
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    # We just need a simple window to capture key presses
    # This line now works because we imported numpy as np
    control_window = np.zeros((200, 400, 3), dtype=np.uint8)
    
    try:
        print("\n--- Bittle Live Driver ---")
        print("INFO: Click on the 'Bittle Remote Control' window.")
        print("CONTROLS:")
        print("  w = Walk Forward (1 step)")
        print("  a = Turn Left (1 sharp step)")
        print("  d = Turn Right (1 sharp step)")
        print("  s = Balance / Stop")
        print("  q = Quit and Rest")
        print("--------------------------")
        
        bittle_serial.write(BALANCE)
        
        while True:
            # Display the control window
            window_copy = control_window.copy()
            cv2.putText(window_copy, "Click Here & Use Keys", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(window_copy, "w: Fwd, a: Left, d: Right, s: Stop, q: Quit", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("Bittle Remote Control", window_copy)
            
            key = cv2.waitKey(1) & 0xFF

            command_to_send = None
            
            if key == ord('w'):
                command_to_send = WALK_FORWARD
                print("Sent: Walk Forward")
            elif key == ord('a'):
                command_to_send = TURN_LEFT
                print("Sent: Turn Left")
            elif key == ord('d'):
                command_to_send = TURN_RIGHT
                print("Sent: Turn Right")
            elif key == ord('s'):
                command_to_send = BALANCE
                print("Sent: Balance / Stop")
            elif key == ord('q'):
                print("Quit command received.")
                break # Exit the loop
            
            if command_to_send:
                bittle_serial.write(command_to_send)
                # Give the robot a moment to process before the next key press
                time.sleep(0.5)

    finally:
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(REST)
            bittle_serial.close()
            print("Serial port closed.")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
