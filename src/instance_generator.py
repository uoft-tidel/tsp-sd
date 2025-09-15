## convert regular TSP into TSP-SAD
import json
import os
import random
import math

folderpath = os.getcwd()
instance_folder = os.path.join(folderpath,"instances","random")
# instance_folder = os.path.join(folderpath,"instances","selected_and_quintiles",batch)


# instances = [f for f in os.listdir(instance_folder)]
instance = "random-50-2.00-0.json"
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

        for p_card in [0,0.1,0.2,0.3,0.4,0.5]:
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

            #calculate AVD
            AVD = 0
            #FEELS WRONG. DOUBLE CHECK #TODO
            for l in range(1,n+1):
                expected_del = sum(1-math.prod(((n-l)-i)/(n-i) for i in range(0,len(Aij[edge]))) for edge in Aij)
                expected_add = sum(math.prod(((n-l)-i)/(n-i) for i in range(0,len(Aij[edge]))) for edge in Aij)
                d_l = (2/n)*(n*(n-1) - expected_del + expected_add)

                AVD += (1/n)*d_l

            i += 1 #index of instance
            print(i, AVD)
            instance_dict[i] = {"p_static": p_static, "p_add": p_add, "p_card": p_card, "Ai": Ai, "Di": Di, "AVD": AVD}

# with open('tsp-sad-50.json', 'w', encoding='utf-8') as f:
#     json.dump(instance_dict, f, ensure_ascii=False, indent=4)