from route_generator import iter_all_white_points, new_find_path, draw_waypoint, rdp_algorithm

import cv2
import numpy as np


########## main ##########


Town = 1
town_name = None
# 1, 4, 10

if Town == 10:
    waypoint_map = cv2.imread("./waypoint_maps/Town10HD.png", 1)
    town_name = "Town10HD"
else:
    town_name = f"Town0{Town}"
    waypoint_map = cv2.imread(f"./waypoint_maps/{town_name}.png", 1)

# (1806, 2507) (1834, 2506)
start, end = (686, 3760), (2491, 4470)
action = "Forward"

all_whites_pos = iter_all_white_points(waypoint_map)


new_img = waypoint_map.copy()
new_img[start[0]][start[1]] = np.array([0, 0, 255])
new_img[end[0]][end[1]] = np.array([0, 0, 255])

cv2.circle(new_img, start, radius=5, color=(255, 0, 0), thickness=3)
cv2.circle(new_img, end, radius=5, color=(255, 0, 0), thickness=3)


print("Start point:", start)
print("End point:", end)
print("Finding Path...")
# final_path = find_path(start, end, all_whites_pos)
final_path = new_find_path(start, end, all_whites_pos, action, True)
print(final_path)

# cv2.imwrite("se.png", new_img)

print("Drawing Waypoint...")
draw_img = draw_waypoint(waypoint_map, start, end, final_path[0])

print("Executing RDP algorithm to get route segment...")
rdp_img, _ = rdp_algorithm(draw_img, final_path[0])

# cv2.imwrite(f"Town{town}_route_result.png", rdp_img)
cv2.imwrite(f"test___{start}_{end}.png", draw_img)