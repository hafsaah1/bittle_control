# vision_triggered_triangle_drawer.py
# This script uses your working shape detector and waits for a spacebar press
# to trigger your calibrated triangle drawing sequence.

import cv2
import numpy as np
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

# --- YOUR CALIBRATED TRIANGLE PROGRAM ---
# This is the exact sequence you discovered using the live driver.
YOUR_TRIANGLE_SEQUENCE = [
    WALK_FORWARD,
    BALANCE,
    TURN_LEFT,
    BALANCE,
    WALK_FORWARD,
    BALANCE,
    TURN_LEFT,
    BALANCE,
    WALK_FORWARD,
    BALANCE,
]

# --- YOUR WORKING SHAPE DETECTOR FUNCTION ---
# This is the get_shape_name function from your working detector script.
def get_shape_name(contour):
    """
    Analyzes a contour and returns the name of a basic shape
    (Triangle, Square, Rectangle, Circle) or None.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0 or area < 500: # Added an area check here
        return None
        
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    num_vertices = len(approx)

    if circularity > 0.70 and num_vertices > 8: 
        return "Circle"
    
    if num_vertices == 3:
        return "Triangle"
    elif num_vertices == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if 0.95 <= aspect_ratio <= 1.05:
            return "Square"
        else:
            return "Rectangle"
            
    return None

def connect_to_bittle():
    """Tries to connect to the serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Successfully connected to Bittle on {SERIAL_PORT}")
        time.sleep(2)
        ser.write(BALANCE)
        print("Bittle standing by.")
        return ser
    except serial.SerialException as e:
        print(f"Error: Could not connect to {SERIAL_PORT}. Details: {e}")
        return None

def execute_drawing(bittle_serial, sequence):
    """Function to make the Bittle draw a sequence."""
    print(f"Executing sequence ({len(sequence)} steps)...")
    for i, command in enumerate(sequence):
        print(f"--> Sending step {i+1}: {command.decode().strip()}")
        bittle_serial.write(command)
        time.sleep(2.0)
    print("\n--- Drawing Complete! ---")
    bittle_serial.write(BALANCE)

def main():
    bittle_serial = connect_to_bittle()
    if not bittle_serial: return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        if bittle_serial: bittle_serial.close()
        return

    print("\n--- Vision-Triggered Triangle Drawer ---")
    print("INFO: Position a triangle in the green box.")
    print("INFO: Press the SPACEBAR to detect and draw.")
    print("INFO: Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Define and draw the Region of Interest (ROI)
        frame_height, frame_width, _ = frame.shape
        roi_size = 400
        x1 = (frame_width - roi_size) // 2
        y1 = (frame_height - roi_size) // 2
        cv2.rectangle(frame, (x1, y1), (x1 + roi_size, y1 + roi_size), (0, 255, 0), 2)
        cv2.putText(frame, "Position Triangle, Press SPACE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Bittle Shape Trigger", frame)

        key = cv2.waitKey(1) & 0xFF

        # --- Wait for user to press the spacebar ---
        if key == ord(' '):
            print("\nSpacebar pressed! Analyzing frame for a triangle...")
            
            roi = frame[y1:y1+roi_size, x1:x1+roi_size]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            found_triangle = False
            for cnt in contours:
                if get_shape_name(cnt) == "Triangle":
                    print(">>> TRIANGLE FOUND! Starting program. <<<")
                    execute_drawing(bittle_serial, YOUR_TRIANGLE_SEQUENCE)
                    found_triangle = True
                    break 
            
            if not found_triangle:
                print("--- No triangle found in that snapshot. Please adjust and try again. ---")

        elif key == ord('q'):
            break
            
    finally:
        print("Shutting down...")
        if bittle_serial and bittle_serial.is_open:
            bittle_serial.write(REST)
            bittle_serial.close()
        cap.release()
        cv2.destroyAllWindows()

# This is the "main" part of the script.
# When you run "python your_file.py", this is the code that starts everything.
if __name__ == "__main__":
    main()

