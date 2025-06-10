# shape_detector.py
import cv2
import numpy as np

def get_shape_name(contour):
    """Analyzes a contour and returns the name of its shape."""
    # Approximate the contour to a polygon
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    
    num_vertices = len(approx)
    
    # Check for common shapes by the number of vertices
    if num_vertices == 3:
        return "Triangle"
    elif num_vertices == 4:
        # To be more precise, you could check the aspect ratio
        # to distinguish between a square and a rectangle
        return "Square"
    elif num_vertices == 5:
        return "Pentagon"
    else:
        return "Circle or Complex Shape"

# --- Main Program ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    # Convert the frame to grayscale and then to a binary (black & white) image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blur the image to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Use a threshold to create a pure black and white image
    _, threshold = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours (outlines) in the binary image
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        # Only process contours of a certain size to ignore noise
        if cv2.contourArea(cnt) > 500:
            shape_name = get_shape_name(cnt)
            
            # Find the center of the contour to place the text
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Draw the contour and the shape name on the original frame
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                cv2.putText(frame, shape_name, (cx - 40, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Shape Detector", frame)
    # You can also uncomment the line below to see the black & white thresholded view
    # cv2.imshow("Threshold", threshold)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()