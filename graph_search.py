import networkx as nx
import numpy as np
import cv2
import json
import networkx as nx
import re
import argparse

from route_generator import iter_all_white_points, draw_waypoint, rdp_algorithm


def find_closest_end_waypoint(original_point, all_whites):
    
    min_idx = -1
    idx = 0
    cur_dis = 1000000
    for white in all_whites:
        delta_x = original_point[0] - white[0]
        delta_y = original_point[1] - white[1]
        dis = (delta_x**2 + delta_y**2)**0.5

        if dis < cur_dis:
            min_idx = idx
            cur_dis = dis

        idx += 1

    closest_end_waypoint = all_whites[min_idx]

    return closest_end_waypoint


def graph_search_path(graph, start, end):
    
    # if start not in G.nodes():
    #     print("start")
    
    # if end in G.nodes():
    #     print("end")

    try:
        path = nx.shortest_path(graph,  start,  end)
    except:
        path = None

    # if start == (1470, 1923) and end == (1274, 2322):
    #     print(path)

    #     exit()

    return path
     

def carla_to_pixel(x, y):
    # Pixel coordinates on full map
    pix_x = int(10.0 * (x - min_x))
    pix_y = int(10.0 * (y - min_y))
    return [pix_x, pix_y]


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


if __name__ == '__main__':

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--town', default=10, choices=[1, 2, 3, 10], type=int)
    # args = parser.parse_args()

    #################################### Read File #############################################

    # Town = args.town
    Town = int(input("Enter town number: 1, 2, 3, or 10\n"))

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

    ########################################################################################
    
    import glob
    import os

    # if glob.glob('graph_list/*'):
    #     list_of_files = glob.glob('graph_list/*')
    #     latest_file = max(list_of_files, key=os.path.getctime)
    #     file_name = latest_file[11:]
    #     idx = int(latest_file[21:-8])

    #     file_name = f"{Town}_graph_v{idx}.adjlist"
    #     G = read_adjlist_with_tuples(f"./graph_list/{file_name}")

    # else:
    #     G = nx.DiGraph()
    #     file_name = f"{Town}_graph_v0.adjlist"

    list_of_files = glob.glob(f'graph_list/{town_name}/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    if Town == 10:
        index = int(latest_file[30:-8])
        new_file_name = latest_file[:30] + str(index+1) + latest_file[-8:]
    else:
        index = int(latest_file[27:-8])
        new_file_name = latest_file[:27] + str(index+1) + latest_file[-8:]

    print(latest_file)
    _ = input("Keep going?\n")

    G = read_adjlist_with_tuples(latest_file)

    count = 0
    lane_change = []
    not_found = []

    all_whites_pos = iter_all_white_points(waypoint_map)

    for white in all_whites_pos[:]: 

        draw_map = waypoint_map.copy()
        bgr_color = instance_map[white[0]][white[1]]
        bgr_string = f'{bgr_color[0]}_{bgr_color[1]}_{bgr_color[2]}'

        if bgr_string in goal_data.keys():
            num_of_goals = goal_data[bgr_string]["num_of_goals"]
            for number in range(num_of_goals):
                action = goal_data[bgr_string][str(number)]['action']
                loc = goal_data[bgr_string][str(number)]['loc']
                goal_pos = carla_to_pixel(loc[0], loc[1])

                ###################### search path #########################
                start = (white[0], white[1])
                end = (goal_pos[1], goal_pos[0])

                # print(start, end)
                
                new_end = find_closest_end_waypoint(end, all_whites_pos)

                if action == "Right Lane Change" or action == "Left Lane Change":
                    lane_change.append([start, new_end, action])
                    # print(f'# {len(lane_change)} lane change')
                    continue

                # start, new_end = (1656, 444), (1452, 446)
                # print(start, new_end)
                path = graph_search_path(G, start, new_end)
                # print(path)
                # exit()

                if path is None:
                    # if not (new_end == (1452, 446) or new_end == (1309, 2322) or new_end == (2013, 481) or new_end == (2032, 450) or new_end == (1434, 1066) or new_end == (2013, 481) or new_end == (1990, 1068) or new_end == (2127, 534)):
                    not_found.append([start, new_end, action, bgr_string])
                    print(f'# {len(not_found)} Not found')
                    continue

                # print(path)
                draw_img = draw_waypoint(draw_map, start, new_end, path)
                rdp_img, _ = rdp_algorithm(draw_img, path)

                if count % 10 == 5:
                    cv2.imwrite(f"./tmp_result/{town_name}/{count}_{start}_{new_end}.png", rdp_img)


        print(f"{count} / {len(all_whites_pos)}")
        count += 1


    ######################################### Store Not found node #########################################
    fp1 = f"{Town}_not_found.txt"
    with open(fp1, 'w') as f:
        for item in not_found:
            f.write(str(item) + '\n')

    fp2 = f"{Town}_lane_change.txt"
    with open(fp2, 'w') as ff:
        for item in lane_change:
            ff.write(str(item) + '\n')