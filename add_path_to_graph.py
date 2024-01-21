import networkx as nx
import re
import os
import glob

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

def add_path(G, path, store_file_name):

    for i in range(len(path[0])-1):
            try:
                G[path[0][i]][path[0][i+1]]
            except:
                print("Add")
            G.add_edge(path[0][i], path[0][i+1])
            

    
    new_path = [path[0][0]]

    for i in range(1, len(path[0])-1):
        # if i%4 == 1 or i%4 == 2:
        if i%3 == 1:
            new_path.append(path[0][i])

    new_path.append(path[0][-1])
    path = new_path.copy()
    path = [path]

    for i in range(len(path[0])-1):
        try:
            G[path[0][i]][path[0][i+1]]
        except:
            print("Add")
        G.add_edge(path[0][i], path[0][i+1])


    nx.write_adjlist(G, store_file_name)
    
    fp = nx.shortest_path(G,  path[0][0],  path[0][-1])
    print(fp)




