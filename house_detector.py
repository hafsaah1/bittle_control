# house_shape_detector.py
import cv2
import numpy as np

def is_house_shape(contour):
    """
    Analyzes a contour to determine if it represents a house shape.
    Returns True if the shape resembles a house, False otherwise.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0 or area < 2000:  
        return False
    
    # Approximate the contour to reduce noise - MUCH more aggressive smoothing
    epsilon = 0.04 * perimeter  
    approx = cv2.approxPolyDP(contour, epsilon, True)
    num_vertices = len(approx)
    
  
    print(f"Shape found - Vertices: {num_vertices}, Area: {area:.0f}")
    

    # triangle roof + rectangle base = 5 vertices minimum
    # REJECT squares and rectangles (4 vertices) to reduce false positives
    if num_vertices < 5 or num_vertices > 8:
        return False
    
    # Calculate bounding rectangle properties
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h
    
    # Houses are typically wider than they are tall
    if aspect_ratio < 0.7 or aspect_ratio > 1.8:  
        print(f"  Rejected: Bad aspect ratio {aspect_ratio:.2f}")
        return False
    
    # Check if the shape has a distinctive "house-like" structure
 
    if has_roof_structure(approx) and num_vertices >= 5:
        print(f"  HOUSE DETECTED! Vertices: {num_vertices}, Aspect: {aspect_ratio:.2f}")
        return True
    else:
        print(f"  Rejected: No roof structure or wrong vertex count")
        return False

def has_roof_structure(approx_contour):
    """
    Checks if the approximated contour has a roof-like structure
    by analyzing the y-coordinates of vertices - MUCH STRICTER VERSION
    """
    if len(approx_contour) < 5:
        return False
    
    # Get all y-coordinates of vertices
    y_coords = [point[0][1] for point in approx_contour]
    
    # Find the topmost point(s)
    min_y = min(y_coords)
    max_y = max(y_coords)
    height = max_y - min_y
    
    # STRICTER: Need significant height difference for a roof
    if height < 50: 
        return False
    
    # Count how many points are in the top 20% of the shape (STRICTER)
    top_threshold = min_y + (height * 0.2) 
    top_points = sum(1 for y in y_coords if y <= top_threshold)
    
    # Count how many points are in the bottom 60% of the shape (STRICTER)
    bottom_threshold = min_y + (height * 0.4)  
    bottom_points = sum(1 for y in y_coords if y >= bottom_threshold)
    

    has_peak = top_points >= 1 and top_points <= 2  
    has_base = bottom_points >= 3  
    
   
    top_point_x = None
    for i, point in enumerate(approx_contour):
        if point[0][1] == min_y:  # Found the topmost point
            top_point_x = point[0][0]
            break
    
    if top_point_x is not None:
        # Get the width of the bounding box
        x_coords = [point[0][0] for point in approx_contour]
        width = max(x_coords) - min(x_coords)
        center_x = min(x_coords) + width / 2
        
        # Top point should be within 30% of center
        if abs(top_point_x - center_x) > width * 0.3:
            return False
    
    return has_peak and has_base

def get_house_confidence(contour):
    """
    Returns a confidence score (0-100) for how house-like a shape is.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0 or area < 500:
        return 0
    
    epsilon = 0.02 * perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)
    num_vertices = len(approx)
    
    confidence = 0
    
    # Vertex count scoring (5-7 vertices are most house-like)
    if num_vertices == 5:
        confidence += 40  # Pentagon (classic house shape)
    elif num_vertices == 6:
        confidence += 35  # Hexagon
    elif num_vertices == 7:
        confidence += 30  # Heptagon
    elif num_vertices == 4:
        confidence += 0   # RECTANGLES/SQUARES GET NO POINTS - they're not houses!
    elif num_vertices == 8:
        confidence += 25  # Octagon
    else:
        confidence += 0   # Other shapes get no points
    
    # Aspect ratio scoring
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h
    if 0.8 <= aspect_ratio <= 1.8:
        confidence += 30  # Good house proportions
    elif 0.6 <= aspect_ratio <= 2.2:
        confidence += 20  # Acceptable proportions
    else:
        confidence += 5   # Poor proportions
    
    # Roof structure scoring
    if has_roof_structure(approx):
        confidence += 40  # INCREASED from 30 - roof structure is critical for houses
    else:
        confidence -= 20  # PENALTY for shapes without roof structure
    
    return min(confidence, 100)  # Cap at 100%

# --- Main Program ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("\n--- Starting House Shape Detector ---")
print("INFO: Point objects at the camera to detect house-like shapes.")
print("INFO: Watch the TERMINAL for detection details.")
print("Press 'q' to quit, 's' to toggle sensitivity")

# Detection sensitivity (can be adjusted)
min_confidence = 85  # MUCH HIGHER - was 70, now 85
show_all_detections = False  # Show all shapes or just high-confidence ones

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame_height, frame_width, _ = frame.shape
    roi_size = 450  # Slightly larger ROI for house detection
    x1 = (frame_width - roi_size) // 2
    y1 = (frame_height - roi_size) // 2
    x2 = x1 + roi_size
    y2 = y1 + roi_size
    
    # Draw ROI rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    roi = frame[y1:y2, x1:x2]

    # Image processing
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Use adaptive threshold for better edge detection
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    house_detected = False
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 1500:  # HIGHER minimum area - was 800
            confidence = get_house_confidence(cnt)
            
            if confidence >= min_confidence or show_all_detections:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"]) + x1
                    cy = int(M["m01"] / M["m00"]) + y1
                    
                    # Color coding based on confidence
                    if confidence >= 80:
                        color = (0, 255, 0)    # Green - High confidence
                        text = f"HOUSE! ({confidence}%)"
                        house_detected = True
                    elif confidence >= min_confidence:
                        color = (0, 165, 255)  # Orange - Medium confidence
                        text = f"House? ({confidence}%)"
                        house_detected = True
                    else:
                        color = (0, 0, 255)    # Red - Low confidence
                        text = f"Shape ({confidence}%)"
                    
                    # Draw contour and label
                    cv2.drawContours(frame, [cnt + [x1, y1]], -1, color, 2)
                    cv2.putText(frame, text, (cx - 60, cy), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
   
    status_text = "HOUSE DETECTED!" if house_detected else "Scanning..."
    status_color = (0, 255, 0) if house_detected else (255, 255, 255)
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
   
    cv2.putText(frame, f"Min Confidence: {min_confidence}%", (10, frame_height - 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Show All: {'ON' if show_all_detections else 'OFF'}", 
                (10, frame_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "Press 's' to toggle sensitivity", (10, frame_height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("House Shape Detector", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        show_all_detections = not show_all_detections
        print(f"Show all detections: {'ON' if show_all_detections else 'OFF'}")
        
cap.release()
cv2.destroyAllWindows()