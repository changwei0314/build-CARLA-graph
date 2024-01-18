import networkx as nx
import numpy as np
import cv2
import json
import networkx as nx
import re
import argparse
import glob
import os

from route_generator import iter_all_white_points, draw_waypoint, rdp_algorithm, recorded_find_path
from add_path_to_graph import add_path, read_adjlist_with_tuples


town_name = f"Town03"
waypoint_map = cv2.imread(f"./waypoint_maps/{town_name}.png", 1)


file1 = open("./3_not_found.txt", 'r')
Lines = file1.readlines()
 
count = 0
# Strips the newline character
for line in Lines:
    count += 1
    # print("Line{}: {}".format(count, line.strip()))
    
    
    ####
    
    ##################### Read latest graph list of the given town #####################

    list_of_files = glob.glob(f'graph_list/{town_name}/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    index = int(latest_file[27:-8])
    new_file_name = latest_file[:27] + str(index+1) + latest_file[-8:]

    G = read_adjlist_with_tuples(latest_file)
    

    start_end_string = line.strip()

    # ##################### Input line in the {town}_not_found.txt #####################

    # start_end_string = input("Enter each list with start-end point in the not found list")

    # # Example input:
    # # [(547, 645), (3871, 1346), 'Forward', '45_45_196']


    entries = re.findall(r'\([^)]+\)', start_end_string)
    start = entries[0]
    start = start.strip('() ')
    x0, y0 =  map(int, start.split(','))
    first_tuple = tuple([x0, y0])

    end = entries[1]
    end = end.strip('() ')
    x, y =  map(int, end.split(','))
    second_tuple = tuple([x, y])

    print(latest_file)
    print(index)
    print(first_tuple)
    print(second_tuple)
    
    
    # start, end = (4596, 3900), (4630, 2197)

    try:
        fp = nx.shortest_path(G,  first_tuple,  second_tuple)
    except:
        
        all_whites_pos = iter_all_white_points(waypoint_map)
        start = first_tuple
        end = second_tuple

        new_img = waypoint_map.copy()
        new_img[start[0]][start[1]] = np.array([0, 0, 255])
        new_img[end[0]][end[1]] = np.array([0, 0, 255])

        cv2.circle(new_img, start[::-1], radius=5, color=(0, 0, 255), thickness=5)
        cv2.circle(new_img, end[::-1], radius=5, color=(255, 255, 0), thickness=5)


        print("Start point:", start)
        print("End point:", end)
        print("Finding Path...")
        # final_path = find_path(start, end, all_whites_pos)
        flag, final_path = recorded_find_path(start, end, all_whites_pos, "", True)

        ##### Path not found #####
        if flag == False:
            print("Not found!!!")
            print(final_path)
            for i, j in final_path[0]:
                new_img[i][j] = np.array([255, 255, 0])
            
            
            cv2.imwrite(f"test/not_found/test__{start}_{end}.png", new_img)
        else:
            print("found!!!")
            print(final_path[0])
            print("Adding to the graph list...")
            
            add_path(G, final_path, new_file_name)
            print(new_file_name, "Store!")
            
            draw_img = draw_waypoint(waypoint_map, start, end, final_path[0])
            rdp_img, _ = rdp_algorithm(draw_img, final_path[0])
            cv2.imwrite(f"test/found/test__{start}_{end}.png", new_img)



            
    # ####