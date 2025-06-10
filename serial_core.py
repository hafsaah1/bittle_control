import cv2
import numpy as np
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Color Detection Configuration (HSV Color Space) ---
## ADDED: Definitions for all your colors ##
# For Red (we check two ranges for better accuracy)
lower_red_1 = np.array([0, 100, 100])
upper_red_1 = np.array([10, 255, 255])
lower_red_2 = np.array([170, 100, 100])
upper_red_2 = np.array([180, 255, 255])

# For Yellow
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])

# For Blue
blue_lower = np.array([90, 100, 100])
blue_upper = np.array([130, 255, 255])

# For Green
green_lower = np.array([40, 70, 70])
green_upper = np.array([80, 255, 255])

# For White
white_lower = np.array([0, 0, 180])
white_upper = np.array([180, 40, 255])


def connect_to_bittle():
    """Tries to connect to the serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Successfully connected to Bittle on {SERIAL_PORT}")
        time.sleep(2)
        ser.write(b'kbalance\n')
        print("Bittle standing by.")
        return ser
    except serial.SerialException as e:
        print(f"Error: Could not connect to {SERIAL_PORT}. Details: {e}")
        return None

def main():
    bittle_serial = connect_to_bittle()
    if not bittle_serial:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        bittle_serial.close()
        return

    last_command_time = time.time()
    command_interval = 1.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            ## ADDED: Masks and contours for all 5 colors ##
            mask_r1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
            mask_r2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
            red_mask = mask_r1 + mask_r2
            
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            white_mask = cv2.inRange(hsv, white_lower, white_upper)
            
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            command = None
            
            ## MODIFIED: The if/elif/else block now matches your new requirements ##
            # The order matters. The first color it finds in this list is the command it will use for that frame.
            
            if red_contours and cv2.contourArea(max(red_contours, key=cv2.contourArea)) > 500:
                command = b'kwkF\n'  # Command: Walk Forward
                cv2.putText(frame, "COMMAND: FORWARD (Red)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            elif yellow_contours and cv2.contourArea(max(yellow_contours, key=cv2.contourArea)) > 500:
                command = b'ktrR\n'  # Command: Trot Right
                cv2.putText(frame, "COMMAND: RIGHT (Yellow)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            elif blue_contours and cv2.contourArea(max(blue_contours, key=cv2.contourArea)) > 500:
                command = b'ktrL\n'  # Command: Trot Left
                cv2.putText(frame, "COMMAND: LEFT (Blue)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            elif green_contours and cv2.contourArea(max(green_contours, key=cv2.contourArea)) > 500:
                command = b'kbkF\n'  # Command: Backward
                cv2.putText(frame, "COMMAND: BACKWARDS (Green)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            elif white_contours and cv2.contourArea(max(white_contours, key=cv2.contourArea)) > 500:
                command = b'krest\n' # Command: Rest
                cv2.putText(frame, "COMMAND: REST (White)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

            else:
                command = b'kbalance\n' # Command: Balance/Stop
                cv2.putText(frame, "COMMAND: STANDBY", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)

            # Send command to Bittle at a controlled rate
            if command and (time.time() - last_command_time > command_interval):
                print(f"Sending command: {command.decode().strip()}")
                bittle_serial.write(command)
                last_command_time = time.time()

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