import cv2
import numpy as np


Town = 3
town_name = None
# 1, 4, 10

if Town == 10:
    waypoint_map = cv2.imread("./waypoint_maps/Town10HD.png", 1)
    town_name = "Town10HD"
else:
    town_name = f"Town0{Town}"
    waypoint_map = cv2.imread(f"./waypoint_maps/{town_name}.png", 1)


# path = [(3664, 2052), (3668, 2052), (3672, 2052), (3708, 2053), (3744, 2053), (3851, 2053), (3964, 2090), (3968, 2093), (3969, 2105), (3969, 2117), (3970, 2128), (3969, 2141), (4004, 2230), (4004, 2247), (4004, 2263), (4004, 2281), (4003, 2343), (4001, 2451), (4000, 2559), (3998, 2667), (3997, 2755)]

# for i, j in path[:]:
#     waypoint_map[i][j] = np.array([255, 255, 0])


start, end = (621, 2364), (604, 1679)

cv2.circle(waypoint_map, start[::-1], radius=5, color=(255, 0, 0), thickness=5)
cv2.circle(waypoint_map, end[::-1], radius=5, color=(0, 255, 0), thickness=5)


cv2.imwrite(f"vis_{start}_{end}.png", waypoint_map)

# print(path[0][:-45])