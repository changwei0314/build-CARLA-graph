import cv2
import numpy as np

# Global variables
zoom_scale = 1.0
shift_x, shift_y = 0, 0
freeze_image = False
window_name = 'image'
stored_pixel_values = []
draw_img = None  # Separate image for drawing

#################################################################################################################

def zoom_image(image, zoom_factor, shift_x, shift_y):
    height, width = image.shape[:2]

    # Calculate new dimensions
    new_width, new_height = int(width * zoom_factor), int(height * zoom_factor)

    # Resize the image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    # Calculate cropping area, adjusted for shifts
    start_x = int(min(max(shift_x, 0), new_width - width))
    start_y = int(min(max(shift_y, 0), new_height - height))

    # Crop the image
    cropped = resized[start_y:start_y + height, start_x:start_x + width]
    return cropped

def mouse_callback(event, x, y, flags, param):
    global stored_pixel_values, draw_img, zoom_scale, shift_x, shift_y

    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:  # Scroll up to zoom in
            zoom_scale *= 1.25
        elif flags < 0:  # Scroll down to zoom out
            zoom_scale *= 0.8
        zoom_scale = max(1.0, zoom_scale)  # Prevent zooming out too much

    if event == cv2.EVENT_LBUTTONDOWN:
        # Adjust x and y based on shifts and zoom scale
        adjusted_x = (x + shift_x) / zoom_scale
        adjusted_y = (y + shift_y) / zoom_scale

        if 0 <= adjusted_x < original_img.shape[1] and 0 <= adjusted_y < original_img.shape[0]:
            pixel_value = original_img[int(adjusted_y), int(adjusted_x)]
            
            # Draw a circle on the drawing image
            if np.all(pixel_value == np.array([255, 255, 255])):
                stored_pixel_values.append((int(adjusted_y), int(adjusted_x)))
                print(f"Clicked Pixel Value at ({int(adjusted_y)}, {int(adjusted_x)}): {pixel_value}")
                cv2.circle(draw_img, (x, y), 3, (0, 255, 0), -1)  # Green circle

def read_adjlist_with_tuples(file_path):
    G = nx.DiGraph()
    with open(file_path, 'r') as file:
        for line in file:
            entries = re.findall(r'\([^)]+\)', line)
            if len(entries) == 0:
                continue
            
            start = entries[0]
            start = start.strip('() ')
            x0, y0 =  map(int, start.split(','))
            start_tuple = tuple([x0, y0])
            
            for entry in entries[1:]:
                end = entry
                end = end.strip('() ')
                x, y =  map(int, end.split(','))
                second_tuple = tuple([x, y])
                G.add_edge(start_tuple, second_tuple)

    return G


#################################################################################################################

import networkx as nx
import re
import os
import glob

# list_of_files = glob.glob('graph_list/*') # * means all if need specific format then *.csv
# latest_file = max(list_of_files, key=os.path.getctime)
# file_name = latest_file[11:]

# count = int(latest_file[21:-8])
# file_name = f"10_graph_v{count}.adjlist"
# G = read_adjlist_with_tuples(f"./graph_list/{file_name}")

town = int(input("Enter town number: 1, 2, 3, 7, or 10:\n"))

print("#"*50)
print("\nScroll mouse to zoom in our zoom out")
print("Press W, A, S, D to move")
print("Press Q to quit")
print("Press P to store\n")
print("#"*50)


if town == 10:
    waypoint_map = cv2.imread("./waypoint_maps/Town10HD.png", 1)
    town_name = "Town10HD"
else:
    town_name = f"Town0{town}"
    waypoint_map = cv2.imread(f"./waypoint_maps/{town_name}.png", 1)

list_of_files = glob.glob(f'graph_list/{town_name}/*') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)

if town == 10:
    index = int(latest_file[30:-8])
    new_file_name = latest_file[:30] + str(index+1) + latest_file[-8:]
else:
    index = int(latest_file[27:-8])
    new_file_name = latest_file[:27] + str(index+1) + latest_file[-8:]

G = read_adjlist_with_tuples(latest_file)
print(latest_file)

# Load an image
original_img = waypoint_map.copy()
img = original_img.copy()
draw_img = np.zeros_like(original_img)  # Initialize drawing image

# Create a window and set a mouse callback
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, mouse_callback)

while True:
    displayed_img = cv2.addWeighted(img, 1, draw_img, 1, 0)  # Combine the images
    cv2.imshow(window_name, displayed_img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('f'):
        freeze_image = not freeze_image
    elif key == ord('q'):
        break

    if not freeze_image:
        if key == ord('w'):
            shift_y -= 70
        elif key == ord('s'):
            shift_y += 70
        elif key == ord('d'):
            shift_x += 70
        elif key == ord('a'):
            shift_x -= 70

        img = zoom_image(original_img, zoom_scale, shift_x, shift_y)

    # Press p to store the path

    if key == ord('p'):
        for i in range(len(stored_pixel_values)-1):
            first = stored_pixel_values[i]
            second = stored_pixel_values[i+1]
            G.add_edge(first, second)

        # Print all stored pixel values
        print("All stored pixel values:", stored_pixel_values)
        nx.write_adjlist(G, new_file_name)
        stored_pixel_values = []

cv2.destroyAllWindows()

# =======================================================================================================






