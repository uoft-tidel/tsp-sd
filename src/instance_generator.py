## convert regular TSP into TSP-SAD
import json
import os
import random
import math

import networkx as nx
import matplotlib.pyplot as plt

def draw_colored_graph(n, Ai, Aij, Di, Dij, node_positions, node_size=200):
 
    eA = set([(str(i),str(j)) for (i,j) in Aij.keys() if Aij[i,j] != []])
    eD = set([(str(i),str(j)) for (i,j) in Dij.keys() if Dij[i,j] != []])
    eS = set((str(i),str(j)) for i in range(1, n) for j in range(i+1, n+1)) - (eA | eD)


    vA = set([str(i) for i in Ai.keys() if Ai[i] != []])
    vD = set([str(i) for i in Di.keys() if Di[i] != []])
    vAD = vA & vD
    vA -= vAD
    vD -= vAD
    vS = set(str(i) for i in range(1, n+1)) - (vA | vD | vAD)

    # Create graph and add nodes/edges
    G = nx.Graph()
    G.add_nodes_from(vS | vA | vD | vAD)
    G.add_edges_from(eS | eA | eD)

    # blk = (61/255,64/255,91/255)
    # red = (224/255,122/255,95/255)
    # grn = (129/255,178/255,154/255)
    # purple = (242/255,204/255,143/255)

    # blk = (91/255,142/255,125/255)
    # red = (188/255,75/255,81/255)
    # grn = (140/255,179/255,105/255)
    # purple = (244/255,162/255,89/255)

    blk = (32/255,42/255,37/255)
    red = (145/255,47/255,64/255)
    grn = (140/255,179/255,105/255)
    purple = (178/255,152/255,220/255)

    # Assign node colors
    node_colors = []
    for node in G.nodes():
        if node in vS:
            node_colors.append(blk)
        elif node in vA:
            node_colors.append(grn)
        elif node in vD:
            node_colors.append(red)
        elif node in vAD:
            node_colors.append(purple)

    # Use provided positions
    # pos = {node: node_positions[node] for node in G.nodes()}
    
    # Draw nodes
    nx.draw_networkx_nodes(G, node_positions, node_color=node_colors, node_size=node_size)

    edge_sets = [[eA, grn, 'dotted', 0.8], [eD, red, 'solid', 0.8], [eS, blk,'solid', 0.5]]
    # Draw edges by type
    for [edges, color, style, alpha] in edge_sets:
        nx.draw_networkx_edges(G, node_positions, edgelist=edges, edge_color=color, style=style, width=2, alpha=alpha)
    
    # Draw labels
    nx.draw_networkx_labels(G, node_positions, font_color='white')
    
    if len(eA) > 0 and len(eD) > 0 and len(eS) > 0 and len(vA) > 0 and len(vD) > 0 and len(vAD) > 0 and len(vS) > 0:
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
        a=1


folderpath = os.getcwd()
instance_folder = os.path.join(folderpath,"instances","random")
# instance_folder = os.path.join(folderpath,"instances","selected_and_quintiles",batch)


# instances = [f for f in os.listdir(instance_folder)]
instance = "random-20-2.60-0.json"
fname = os.path.join(instance_folder, instance)

with open(fname, 'r') as file:
    instance = json.load(file)

## Generation Method
# If TRUE, then simply reassigns a proportion of original deleted edges to be added instead
# If FALSE, then recreates deletion function by assigning x% of edges to be deleted, y% to be added, and (1-x-y)% to be always available

#CAREFUL OF DUMMY NODE
n = len(instance["NODE_COORDS"].keys()) 
nodes = [i for i in range(1,n+1)]
e = int(n*(n-1)/2)
edges = [(i+1,j+1) for i in range(n) for j in range(n) if i < j]

instance_dict = {}
i = 0
for p_static in range(0,100,10):
    #choose dynamic edges
    p_static /= 100
    p_dynamic = 1-p_static
    e_dynamic = round(p_dynamic * e)

    random.shuffle(edges) #creates random ordering of edges
    dynamic_edges = edges[:e_dynamic] #selects first e_dynamic number of edges to be dynamic

    for p_add_theoretical in range(0,110,10):
        #add dynamic edges to D and A
        p_add_theoretical /= 100
        e_add = round(e_dynamic*p_add_theoretical)
        p_add = e_add/max(1,e_dynamic)
        e_del = e_dynamic-e_add

        random.shuffle(dynamic_edges)

        added_edges = dynamic_edges[:e_add]
        deleted_edges = dynamic_edges[e_add:]

        for p_card in [0.05,0.1,0.2,0.3,0.4,0.5]:
            #add dynamic edges to Di and Ai
            n_card = max(1,int(n*p_card))
            Aij = {}
            Dij = {}
            for edge in added_edges:
                Aij[edge] = random.choices(nodes,k=n_card)
            for edge in deleted_edges:
                Dij[edge] = random.choices(nodes,k=n_card)

            Ai = {i:[] for i in range(1,n+1)}
            Di = {i:[] for i in range(1,n+1)}

            for edge in Aij:
                for node in Aij[edge]:
                    Ai[node].append(edge)
            for edge in Dij:
                for node in Dij[edge]:
                    Di[node].append(edge)

            print(i)
            i += 1
            print(p_dynamic, p_add, p_card)
            draw_colored_graph(n, Ai, Aij, Di, Dij, instance["NODE_COORDS"])

            # #calculate AVD
            # AVD = 0
            # #FEELS WRONG. DOUBLE CHECK #TODO
            # for l in range(1,n+1):
            #     expected_del = sum(1-math.prod(((n-l)-i)/(n-i) for i in range(0,len(Dij[edge]))) for edge in Dij)
            #     expected_add = sum(1-math.prod(((n-l)-i)/(n-i) for i in range(0,len(Aij[edge]))) for edge in Aij)
            #     expected_add = 0
            #     d_l = (2/n)*(n*(n-1) - expected_del + expected_add)

            #     AVD += d_l

            # AVD /= n

            # i += 1 #index of instance
            # print(i, AVD)
            #instance_dict[i] = {"p_static": p_static, "p_add": p_add, "p_card": p_card, "Ai": Ai, "Di": Di, "AVD": AVD}

            

# with open('tsp-sad-50.json', 'w', encoding='utf-8') as f:
#     json.dump(instance_dict, f, ensure_ascii=False, indent=4)