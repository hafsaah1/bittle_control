# basic_shape_detector.py (v3 - with Debug Print)
import cv2
import numpy as np

def get_shape_name(contour):
    """
    Analyzes a contour and returns the name of a basic shape
    (Triangle, Square, Rectangle, Circle) or None.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0:
        return None
        
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    
    # --- THIS IS THE NEW DEBUG LINE ---
    # It will print the score for any large shape it finds.
    print(f"Detected a shape with circularity score: {circularity:.2f}")

    # --- THIS IS THE LINE WE WILL TUNE ---
    # We are checking if the score is greater than our threshold.
    if circularity > 0.6: # Lowered the threshold even more to start
        return "Circle"
    
    # If not a circle, approximate it to a polygon
    approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
    num_vertices = len(approx)
    
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

# --- Main Program ---
# (The rest of the code is exactly the same as before)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("\n--- Starting Shape Tuner ---")
print("INFO: Watch the TERMINAL to see the circularity scores.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame_height, frame_width, _ = frame.shape
    roi_size = 400
    x1 = (frame_width - roi_size) // 2
    y1 = (frame_height - roi_size) // 2
    x2 = x1 + roi_size
    y2 = y1 + roi_size
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    roi = frame[y1:y2, x1:x2]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            shape_name = get_shape_name(cnt)
            
            if shape_name:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"]) + x1
                    cy = int(M["m01"] / M["m00"]) + y1
                    
                    cv2.putText(frame, shape_name, (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Shape Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()