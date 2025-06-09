import cv2
import numpy as np
import serial  # <-- This script uses 'serial', not 'pyBittle'
import time

# --- Bittle Configuration ---
#
# vvv THIS IS THE LINE YOU NEED TO CHANGE vvv
#
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
#
# ^^^ THIS IS THE LINE YOU NEED TO CHANGE ^^^
#
BAUD_RATE = 115200

# --- Color Detection Configuration (HSV Color Space) ---
# HSV values for Blue
blue_lower = np.array([90, 100, 100])
blue_upper = np.array([130, 255, 255])

# HSV values for Green
green_lower = np.array([40, 70, 70])
green_upper = np.array([80, 255, 255])

def connect_to_bittle():
    """Tries to connect to the serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Successfully connected to Bittle on {SERIAL_PORT}")
        time.sleep(2) # Wait for the connection to establish
        ser.write(b'kbalance\n') # Command Bittle to stand up at the start
        print("Bittle standing by.")
        return ser
    except serial.SerialException as e:
        print(f"Error: Could not connect to {SERIAL_PORT}. Please check:")
        print("1. If the port name is correct.")
        print("2. If Bittle is powered on and connected in your Mac's Bluetooth settings.")
        print("3. If any other program is using the port.")
        print(f"Details: {e}")
        return None

def main():
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return # Exit if connection failed

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        bittle_serial.close()
        return

    last_command_time = time.time()
    command_interval = 1.0 # Send a command every 1 second to avoid spamming

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            current_time = time.time()
            command = None
            
            if blue_contours and cv2.contourArea(max(blue_contours, key=cv2.contourArea)) > 500:
                command = b'ktrL\n' # Command: Trot Left
                cv2.putText(frame, "COMMAND: LEFT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            elif green_contours and cv2.contourArea(max(green_contours, key=cv2.contourArea)) > 500:
                command = b'ktrR\n' # Command: Trot Right
                cv2.putText(frame, "COMMAND: RIGHT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                command = b'kbalance\n' # Command: Balance/Stop
                cv2.putText(frame, "COMMAND: STANDBY", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Send command to Bittle at a controlled rate
            if command and (current_time - last_command_time > command_interval):
                print(f"Sending command: {command.decode().strip()}")
                bittle_serial.write(command)
                last_command_time = current_time

            cv2.imshow("Bittle Vision Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n') # Command Bittle to rest
            bittle_serial.close()
            print("Serial port closed.")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()