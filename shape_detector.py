# simple_shape_finder.py
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
        return "Square"
    else:
        # For simplicity, we'll just focus on triangles and squares for now
        return None

# --- Main Program ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("\n--- Starting Simple Shape Finder ---")
print("INFO: Hold a paper with a dark, clear shape INSIDE the green box.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    # --- Define a Region of Interest (ROI) ---
    frame_height, frame_width, _ = frame.shape
    roi_size = 350 # You can make this box bigger or smaller
    x1 = (frame_width - roi_size) // 2
    y1 = (frame_height - roi_size) // 2
    x2 = x1 + roi_size
    y2 = y1 + roi_size
    
    # Draw the green ROI box on the main frame for guidance
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Create a separate, smaller image that is just the inside of the box
    roi = frame[y1:y2, x1:x2]

    # --- We will now ONLY process the 'roi' image ---
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use a simple threshold. This value might need tuning!
    # Try changing 127 to 100 or 150 if detection is not working.
    _, threshold = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours ONLY within the ROI
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Loop through all found contours
    for cnt in contours:
        # Make sure the contour is of a decent size
        if cv2.contourArea(cnt) > 400:
            shape_name = get_shape_name(cnt)
            
            # If we identified a shape, draw it
            if shape_name:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    # Get the center of the shape within the ROI
                    cx_roi = int(M["m10"] / M["m00"])
                    cy_roi = int(M["m01"] / M["m00"])
                    
                    # Calculate the center on the MAIN frame to draw the text
                    cx_main = cx_roi + x1
                    cy_main = cy_roi + y1
                    
                    cv2.putText(frame, shape_name, (cx_main - 40, cy_main), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Shape Finder", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()