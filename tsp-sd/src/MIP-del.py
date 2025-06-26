#! /usr/bin/env python3

import json, math
import gurobipy as gp
from gurobipy import GRB
import os
import sys
import psutil
process = psutil.Process()

if __name__ == "__main__":
  
    def convertToLatLong(x):
        deg = round(x)
        min = x-deg
        lat = (math.pi*(deg+5*min)/3)/180
        return lat

    def getDistance(p1,p2):
    # RRR = 6378.388
    # q1 = math.cos(convertToLatLong(p1[1]) - convertToLatLong(p2[1]))
    # q2 = math.cos(convertToLatLong(p1[0]) - convertToLatLong(p2[0]))
    # q3 = math.cos(convertToLatLong(p1[0]) + convertToLatLong(p2[0]))
    # dij = round((RRR*math.acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3))+1.0))

        dij = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

        return dij

    def read_file(fpath):

        with open(fpath, 'r') as file:
            instance = json.load(file)

        nodes = [str(i) for i in range(len(instance["NODE_COORDS"])+1)]
        n = len(nodes)
        times = [int(t) for t in range(n-1)]
        dist_dict = {(i,j,t): getDistance(instance["NODE_COORDS"][i],instance["NODE_COORDS"][j]) for i in instance["NODE_COORDS"].keys() for j in instance["NODE_COORDS"].keys() for t in times if i != j}
        
        for i in instance["NODE_COORDS"].keys():
            for t in times:
                dist_dict[('0',i,t)] = 0.0 
        
        #for i in instance["NODE_COORDS"].keys():
        #    dist_dict[(0,i,0)] = 0
        #    dist_dict[(i,n+1,n+1)] = 0
            
        #times = [0] + times + [n+1]

        del_dict = instance["DELETE"]
        
        return dist_dict, del_dict, nodes, times, n

    def main(fpath, time_limit):

        distances, deletes, nodes, times, n = read_file(fpath)

        if n > 101:
            return "TOO MANY NODES - MEMORY OUT"

        all_edges = set()
        for i in range(1,n+1):
            for j in range(i+1,n+1):
                all_edges.add((str(i),str(j)))

        deleted = set(tuple(i) for a in deletes.values() for i in a)
        all_edges = set((str(i),str(j)) for i in range(1,n) for j in range(i+1,n) if i != j)
        never_deleted_edges = all_edges.difference(deleted)
        potential_start_nodes = set(i for j in never_deleted_edges for i in j)



        add_reverse = set(tuple(reversed(i)) for i in never_deleted_edges)
        for i in add_reverse:
            never_deleted_edges.add(i)

        never_deleted_edges_dict = {a: distances[a[0],a[1],1] for a in never_deleted_edges}

        never_deleted_dict = {i: set(j for (k,j) in never_deleted_edges if k == i) for i in potential_start_nodes}

        #try:
        # Create a new model
        m = gp.Model("TSP-SD")

        # Create variables

        x = m.addVars(distances.keys(), obj = distances, vtype = GRB.BINARY, name="x")
        last_edge = m.addVars(never_deleted_edges_dict.keys(), obj = never_deleted_edges_dict, vtype = GRB.BINARY, name="last_edge")


        #z = m.addVars(potential_start_nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1, name="xnor")

        #m.addConstr(gp.quicksum(x['*', j,'*'] for j in nodes) == 1)
        #m.addConstr(gp.quicksum(x[int(j), n+1,n+1] for j in nodes) == 1)

        #FIRST AND LAST EDGES
        m.addConstr(gp.quicksum(x['0',i,0] for i in potential_start_nodes) == 1, name="first")
        m.addConstr(gp.quicksum(x[j,i,n-2] for j in nodes[1:] for i in potential_start_nodes if i != j) == 1, name="last")
        for i in never_deleted_dict:
            #if i is chosen, one of nodes going into available 'last node pair' must be chosen
            m.addConstr(x['0',i,0] <= gp.quicksum(x[k,j,n-2] for k in nodes[1:] for j in never_deleted_dict[i] if k != j), name=f"prune_last_{i}") #only go to allowed end nodes based on start node

        #each node visited once
        for i in nodes[1:]:
            m.addConstr(gp.quicksum(x[j,i,t] for j in nodes for t in times if i != j) == 1)

        for t in times[1:]:
            for i in nodes[1:]:
                m.addConstr(gp.quicksum(x[i, j,t] for j in nodes[1:] if i != j) == gp.quicksum(x[j, i,t-1] for j in nodes if i != j), 
                        name=f"define_rank_node:{i}_time:{t}")


        for t in times[1:]:
            m.addConstr(gp.quicksum(x[i, j,t] for i in nodes for j in nodes[1:] if i != j) == 1, name=f"each time one node - {t}")

        #m.write(r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\test3_2.lp")

        #delete edges (edges can only be visited before they're deleted)
        M = n+1
        for (i, dels) in deletes.items():
            #if int(i) <= 12:
            # for [n1, n2] in dels:
            #     m.addConstr(gp.quicksum(t*x[n1, n2,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j), name="del_1")
            #     m.addConstr(gp.quicksum(t*x[n2, n1,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j), name="del_2")

            #DEL
            for [n1, n2] in dels:
                m.addConstr(gp.quicksum(t*x[n1, n2,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j), name="del_1")
                m.addConstr(gp.quicksum(t*x[n2, n1,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j), name="del_2")

            #ADD
            # for [n1, n2] in dels:
            #     m.addConstr(gp.quicksum(t*x[n1, n2,t] for t in times) + M*(1-gp.quicksum(x[n1, n2,t] for t in times)) >= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j)+1, name="add_1")
            #     m.addConstr(gp.quicksum(t*x[n2, n1,t] for t in times) + M*(1-gp.quicksum(x[n2, n1,t] for t in times)) >= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j)+1, name="add_2")


        #last edge
        for (i,j) in never_deleted_edges:
            m.addConstr(x['0',i,0] + gp.quicksum(x[k,j,n-2] for k in nodes[1:] if k != j) <= last_edge[i,j] + 1)

        # m.write(#"tspsd-TOY.lp")

        m.Params.TimeLimit = time_limit
        m.Params.SoftMemLimit = 8
        m.Params.Threads = 1

        # Optimize model
        m.optimize()

        # for v in m.getVars():
            # if v.X > 0.1:
                # print(f"{v.VarName}") #{v.X:g}")

        # print(never_deleted_ed#ges_dict)
        try:
            print(f"Obj: {m.ObjVal:g}")
            print(f"Time: {m.Runtime:g}")
            print("Memory Used (MiB): {}".format(round(process.memory_info().rss / 1024 ** 2,2)))
        
        except gp.GurobiError as e:
            print(f"Error code {e.errno}: {e}")

        except AttributeError:
            print("Encountered an attribute error")
        return 0

    # toy = r"C:\Users\pekar\Documents\GitHub\tsp-sd\instances\toy.json"
    # burma = r"C:\Users\pekar\Documents\GitHub\tsp-sd\instances\burma14-3.1.json"
    # ulysses = r"C:\Users\pekar\Documents\GitHub\tsp-sd\instances\ulysses22-5.5.json"
    script, timelim, batch = sys.argv

    folderpath = os.getcwd()
    # batch = "1"
    # timelim = "1800"
    # folderpath = r"C:\Users\pekar\Documents\GitHub\TSP-SD"
    instance_folder = os.path.join(folderpath,"instances","random")
    tlim = int(timelim)


    for instance in [i for i in os.listdir(instance_folder) if batch in i]:

        fname = os.path.join(instance_folder, instance)
        # output_path = os.path.join(folderpath,"log", instance[:-5]+"_"+str(tlim)+".log")

        print("===INSTANCE START")
        print("ALG: MIP-DEL")
        print("Instance Name: {}".format(os.path.basename(fname)))
        try:
            main(fname, tlim)
        except Exception as e:
            print("error: ", e)

        print("ALGORITHM END")
        print("---RESULTS END")