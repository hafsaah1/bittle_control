import cv2
import turtle
import numpy as np
import math
from collections import deque
import time

turtle.tracer(0)
turtle.bgcolor("white")

def outline(image):
    """Extract outline from image using adaptive thresholding"""
    src_image = cv2.imread(image, 0)
    blurred = cv2.GaussianBlur(src_image, (7, 7), 0)
    th3 = cv2.adaptiveThreshold(blurred, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                thresholdType=cv2.THRESH_BINARY, blockSize=9, C=2)
    return th3

def douglas_peucker(points, epsilon):
    """Simplify a curve using Douglas-Peucker algorithm"""
    if len(points) <= 2:
        return points
    
    # Find the point with maximum distance from line between start and end
    start, end = points[0], points[-1]
    max_dist = 0
    max_idx = 0
    
    for i in range(1, len(points) - 1):
        dist = point_to_line_distance(points[i], start, end)
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    
    # If max distance is greater than epsilon, recursively simplify
    if max_dist > epsilon:
        # Recursive call
        left = douglas_peucker(points[:max_idx + 1], epsilon)
        right = douglas_peucker(points[max_idx:], epsilon)
        
        # Combine results (avoid duplicate point)
        return left[:-1] + right
    else:
        # Return just start and end points
        return [start, end]

def point_to_line_distance(point, line_start, line_end):
    """Calculate perpendicular distance from point to line"""
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # If line start and end are the same
    if x1 == x2 and y1 == y2:
        return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
    
    # Calculate distance
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    return num / den if den > 0 else 0

def find_contours_cv2(image):
    """Use OpenCV to find contours more efficiently"""
    th3 = outline(image)
    contours, _ = cv2.findContours(th3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Convert to our format
    converted_contours = []
    for contour in contours:
        if len(contour) > 5:  # Only keep significant contours
            points = [(int(point[0][0]), int(point[0][1])) for point in contour]
            converted_contours.append(points)
    
    return converted_contours

def smooth_contour_lines(contour, angle_threshold=15):
    """Combine nearby points into smooth lines based on angle consistency"""
    if len(contour) < 3:
        return contour
    
    smoothed = [contour[0]]
    current_direction = None
    
    for i in range(1, len(contour) - 1):
        prev_point = smoothed[-1]
        current_point = contour[i]
        next_point = contour[i + 1]
        
        # Calculate direction from previous to current
        dx1 = current_point[0] - prev_point[0]
        dy1 = current_point[1] - prev_point[1]
        
        # Calculate direction from current to next
        dx2 = next_point[0] - current_point[0]
        dy2 = next_point[1] - current_point[1]
        
        if dx1 == 0 and dy1 == 0:
            continue
        if dx2 == 0 and dy2 == 0:
            continue
        
        # Calculate angles
        angle1 = math.degrees(math.atan2(dy1, dx1))
        angle2 = math.degrees(math.atan2(dy2, dx2))
        
        # Calculate angle difference
        angle_diff = abs(angle1 - angle2)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # If angle changes significantly, this is a corner point
        if angle_diff > angle_threshold:
            smoothed.append(current_point)
    
    # Always add the last point
    smoothed.append(contour[-1])
    
    return smoothed

def draw_smooth_line(t, start, end):
    """Draw a smooth line from start to end point"""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    if dx == 0 and dy == 0:
        return
    
    # Calculate angle and distance
    angle = math.degrees(math.atan2(dy, dx))
    distance = math.sqrt(dx**2 + dy**2)
    
    # Move to start position
    t.penup()
    t.goto(start)
    t.pendown()
    
    # Set heading and draw line
    t.setheading(angle)
    t.forward(distance)

def draw_contour_smooth(t, contour):
    """Draw a contour as smooth connected lines"""
    if len(contour) < 2:
        return
    
    # Smooth the contour first
    smoothed = smooth_contour_lines(contour, angle_threshold=20)
    
    # Further simplify with Douglas-Peucker
    simplified = douglas_peucker(smoothed, epsilon=8)
    
    if len(simplified) < 2:
        return
    
    # Draw the simplified contour
    t.penup()
    t.goto(simplified[0])
    t.pendown()
    
    for i in range(1, len(simplified)):
        current_pos = t.pos()
        target = simplified[i]
        
        # Calculate angle and move smoothly
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        
        if dx != 0 or dy != 0:
            angle = math.degrees(math.atan2(dy, dx))
            distance = math.sqrt(dx**2 + dy**2)
            
            t.setheading(angle)
            t.forward(distance)

def draw_image(image, x, y):
    """Main function to process and draw image with smooth lines"""
    # Get image dimensions for centering
    im = cv2.imread(image, 0)
    HEIGHT, WIDTH = im.shape
    
    # Find contours using OpenCV
    contours = find_contours_cv2(image)
    
    # Filter and sort contours by area (largest first)
    significant_contours = []
    for contour in contours:
        if len(contour) > 10:  # Only keep contours with enough points
            # Calculate approximate area
            area = cv2.contourArea(np.array(contour).reshape(-1, 1, 2))
            if area > 100:  # Filter out very small contours
                significant_contours.append((area, contour))
    
    # Sort by area (largest first)
    significant_contours.sort(key=lambda x: x[0], reverse=True)
    
    # Setup turtle
    t = turtle.Turtle()
    t.color("black")
    t.width(2)
    t.speed(0)
    
    print(f"Drawing {len(significant_contours)} contours")
    
    # Draw each contour
    for area, contour in significant_contours:
        # Transform coordinates to center the image
        transformed_contour = []
        for point in contour:
            new_x = point[0] - WIDTH / 2 + x
            new_y = -1 * (point[1] - HEIGHT / 2) + y  # Flip Y axis
            transformed_contour.append((new_x, new_y))
        
        draw_contour_smooth(t, transformed_contour)
        turtle.update()
    
    t.hideturtle()

# Configuration
image_files = ['patrick.jpg'] 
image_positions = [(0, 0)]  # Positions for each image

# Draw each image
for image_file, (x, y) in zip(image_files, image_positions):
    draw_image(image_file, x, y)

turtle.done()