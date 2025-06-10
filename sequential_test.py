import cv2
import numpy as np
import serial
import time

# --- Bittle Configuration ---
SERIAL_PORT = '/dev/tty.BittleB3_SSP' 
BAUD_RATE = 115200

# --- Color Definitions ---
COLORS = {
    "red": (np.array([0, 100, 100]), np.array([10, 255, 255])),
    "red_wrap": (np.array([170, 100, 100]), np.array([180, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([30, 255, 255])),
    "blue": (np.array([90, 100, 100]), np.array([130, 255, 255])),
    "green": (np.array([40, 70, 70]), np.array([80, 255, 255])),
    "black": (np.array([0, 0, 0]), np.array([180, 255, 50])) # GO SIGNAL
}

# --- Command Mapping ---
COMMAND_MAP = {
    "red": (b'kwkF\n', "Forward"),
    "yellow": (b'ktrR\n', "Right"),
    "blue": (b'ktrL\n', "Left"),
    "green": (b'kbkF\n', "Backwards")
}

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

def get_dominant_color(hsv_frame):
    """Finds the most prominent color in the frame."""
    max_area = 0
    dominant_color = None

    for color_name, (lower, upper) in COLORS.items():
        if color_name == "red_wrap": continue
        
        mask = cv2.inRange(hsv_frame, lower, upper)
        if color_name == "red":
            mask += cv2.inRange(hsv_frame, COLORS["red_wrap"][0], COLORS["red_wrap"][1])
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            area = cv2.contourArea(max(contours, key=cv2.contourArea))
            if area > max_area:
                max_area = area
                dominant_color = color_name
    
    if max_area > 500:
        return dominant_color
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

    # --- State Machine Variables ---
    # MODIFIED: Added a "COUNTDOWN" state
    currentState = "LISTENING" # Can be "LISTENING", "COUNTDOWN", or "EXECUTING"
    command_queue = []
    program_names = []
    last_detection_time = time.time()
    detection_cooldown = 1.5
    
    ## NEW: Variable to store when the countdown starts ##
    countdown_start_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            detected_color = get_dominant_color(hsv)
            
            if currentState == "LISTENING":
                cv2.putText(frame, "MODE: PROGRAMMING", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Program: {program_names}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if detected_color and (time.time() - last_detection_time > detection_cooldown):
                    if detected_color == 'black':
                        if command_queue:
                            print(f"GO SIGNAL DETECTED! Starting 10-second countdown.")
                            ## MODIFIED: Instead of executing, start the countdown ##
                            countdown_start_time = time.time()
                            currentState = "COUNTDOWN"
                        else:
                            print("Go signal detected, but program is empty!")
                            last_detection_time = time.time()
                    else:
                        command, name = COMMAND_MAP[detected_color]
                        command_queue.append(command)
                        program_names.append(name)
                        print(f"Added '{name}' to program. Queue has {len(command_queue)} steps.")
                        last_detection_time = time.time()
            
            ## NEW STATE: COUNTDOWN ##
            elif currentState == "COUNTDOWN":
                time_elapsed = time.time() - countdown_start_time
                time_remaining = 10 - time_elapsed
                
                # Display the countdown on screen
                countdown_text = f"EXECUTING IN: {int(time_remaining) + 1}"
                cv2.putText(frame, countdown_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                cv2.putText(frame, f"Program: {program_names}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # If the countdown is finished, switch to EXECUTING mode
                if time_remaining <= 0:
                    print("Countdown finished! Executing program...")
                    currentState = "EXECUTING"

                # Optional: Allow canceling the countdown by moving the black object away
                if detected_color != 'black':
                    print("Countdown cancelled! Returning to Programming mode.")
                    currentState = "LISTENING"

            elif currentState == "EXECUTING":
                display_text = f"EXECUTING: {program_names}"
                cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if command_queue:
                    command_to_run = command_queue.pop(0)
                    program_names.pop(0)
                    
                    print(f"--> Executing: {command_to_run.decode().strip()}")
                    bittle_serial.write(command_to_run)
                    time.sleep(3.0)
                else:
                    print("--- Program Complete! Returning to Programming Mode. ---")
                    bittle_serial.write(b'kbalance\n')
                    currentState = "LISTENING"

            cv2.imshow("Bittle Vision Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(b'd\n')
            bittle_serial.close()
            print("Serial port closed.")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()