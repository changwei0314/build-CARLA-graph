import networkx as nx
import numpy as np
import cv2
import json
import networkx as nx
import argparse

from route_generator import iter_all_white_points, new_find_path, draw_waypoint, rdp_algorithm


parser = argparse.ArgumentParser()
parser.add_argument('--town', default=10, choices=[1, 2, 3, 5, 10], type=int)
args = parser.parse_args()

#################################### Read File #############################################

Town = args.town
if Town == 10:
    waypoint_map = cv2.imread("./waypoint_maps/Town10HD.png", 1)
    town_name = "Town10HD"
else:
    town_name = f"Town0{Town}"
    waypoint_map = cv2.imread(f"./waypoint_maps/{town_name}.png", 1)
    

with open('ori_MapBoundaries.json', 'r') as f:
        data = json.load(f)

min_x = data[town_name]['min_x']
min_y = data[town_name]['min_y']

with open(f'./goals/{town_name}.json', 'r') as ff:
        goal_data = json.load(ff)

instance_map = cv2.imread(f"./instance_goal_maps/{town_name}.png")


################################## function #####################################################
        
def pixel_to_carla(self, image):
    min_point = np.array([min_x, min_y])
    image = np.argwhere(image > 0)
    tmp = image.copy()
    image[:,0] = tmp[:, 1]
    image[:,1] = tmp[:, 0]
    waypoints = (image /10.0) + min_point
    
    return waypoints

def carla_to_pixel(x, y):
    # Pixel coordinates on full map
    pix_x = int(10.0 * (x - min_x))
    pix_y = int(10.0 * (y - min_y))
    
    return [pix_x, pix_y]


G = nx.DiGraph() 

def build_graph(path):

    for i in range(len(path)-1):
        first = path[i]
        second = path[i+1]

        G.add_edge(first, second)
    return

##################################################################################################



all_path_list = []
visited_point = dict()

print("Iterating...")
all_whites_pos = iter_all_white_points(waypoint_map)
for white in all_whites_pos:
    visited_point[white] = 0

transfer_goal_dict = dict()


draw_map = waypoint_map.copy()
length = len(all_whites_pos)
count = 0

not_found_list = []
not_found_goal_list = []

for white in all_whites_pos:

    if visited_point[white] == 1:
        continue

    bgr_color = instance_map[white[0]][white[1]]
    bgr_string = f'{bgr_color[0]}_{bgr_color[1]}_{bgr_color[2]}'
    # print(bgr_string)

    if bgr_string in goal_data.keys():

        num_of_goals = goal_data[bgr_string]["num_of_goals"]
        
        for number in range(num_of_goals):
            action = goal_data[bgr_string][str(number)]['action']

            loc = goal_data[bgr_string][str(number)]['loc']
            goal_pos = carla_to_pixel(loc[0], loc[1])
                
            ###################### route generator #########################
            
            start = (white[0], white[1])
            end = (goal_pos[1], goal_pos[0])

            transfer_end = None
            if end in transfer_goal_dict:
                transfer_end = transfer_goal_dict[end]
            else:
                transfer_end = end

            print("Start:", start)
            print("end:", end)

            ################################################################################################
            # Cannot find the path because there is no waypoint between two parallel lane
            if action == "Right Lane Change" or action == "Left Lane Change":
                # print("lane change")
                continue
            if transfer_end in not_found_goal_list:
                not_found_list.append([start, end, action, bgr_string])
                print(f"============= Fail: {len(not_found_list)} =============")
                continue

            ##### First attempt to find path #####
            final_path = new_find_path(start, transfer_end, all_whites_pos, action, False)
            if len(final_path) == 0:
                
                ##### Second attempt to find path #####
                # Reverse search
                print("============= Second Attempt =============")
                final_path = new_find_path(transfer_end, start, all_whites_pos, action, False)
                final_path = final_path[::-1]

                if len(final_path) == 0:
                    ##### Third attempt to find path #####
                    # Global search
                    print("============= Third Attempt =============")
                    global_search = True
                    final_path = new_find_path(transfer_end, start, all_whites_pos, action, global_search)
                    final_path = final_path[::-1]
                    
                    if len(final_path) == 0:
                        not_found_list.append([start, end, action, bgr_string])
                        not_found_goal_list.append(transfer_end)

                        print(f"============= Fail: {len(not_found_list)} =============")
                        continue
                        # print("="*20)
                        # print("Action", action)
                        # print("start = ", start)
                        # print("end = ", end)
                        # print("transfer_end", transfer_end)
                        # print("bgr_string:", bgr_string)
                        # print("="*20)
                        # exit()

            ################################################################################################
            
            if len(final_path[0]) < 3:
                for pts in final_path[0][:]:
                    if visited_point[tuple(pts)] == 0:
                        visited_point[tuple(pts)] = 1
                        count += 1
            else:
                for pts in final_path[0][:-1]:
                    if visited_point[tuple(pts)] == 0:
                        visited_point[tuple(pts)] = 1
                        count += 1
            
            all_path_list.append(final_path[0])
            build_graph(final_path[0])
           
            draw_img = draw_waypoint(draw_map, start, end, final_path[0])
            rdp_img, _ = rdp_algorithm(draw_img, final_path[0])

            draw_map = rdp_img.copy()
            transfer_goal_dict[end] = start

            # print(count, "/", length)

            if len(final_path[0]) > 30:
                cv2.imwrite(f"./tmp_res/Town{Town}_route_{start}_{transfer_end}.png", draw_map)
                print(count, "/", length)
    else:
        # print("instance key not found!!")
        pass
    

nx.write_adjlist(G,f'{Town}_graph_v0.adjlist')

fp1 = f"{Town}_not_found.txt"
with open(fp1, 'w') as f:
    for item in not_found_list:
        f.write(str(item) + '\n')

print(len(not_found_list))
print(count)
