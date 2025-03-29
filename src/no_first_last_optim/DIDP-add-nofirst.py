#! /usr/bin/env python3

import didppy as dp
import math
import json
import os 
import copy
import sys
import validate as vlad
# import visualize as viz
import ntpath
import psutil
process = psutil.Process()

if __name__ == "__main__":

    script, timelim, inst = sys.argv
    # timelim = "1800"
    # batch = "1"
    folderpath = os.getcwd()
    instance_folder = os.path.join(folderpath,"instances","random")
    # instance_folder = os.path.join(folderpath,"instances","selected_and_quintiles",batch)
    tlim = int(timelim)

    for instance in [f for f in os.listdir(instance_folder) if inst in f]:
        print(instance)
        # if "burma14-3.1.json" == instance:
        fname = os.path.join(instance_folder, instance)
        # output_path = os.path.join(folderpath,"log", instance[:-5]+"_"+str(tlim)+".log")

        print("===INSTANCE START")
        print("ALG: DIDP-ADD")
        print("OPT: NO FIRST/LAST")
        print("Instance Name: {}".format(ntpath.basename(fname)))

        with open(fname, 'r') as file:
            instance = json.load(file)

        def convertToLatLong(x):
            deg = round(x)
            minute = x-deg
            lat = (math.pi*(deg+5*minute)/3)/180
            return lat

        def getDistance(instance, p1,p2):
            if p1 == '0' or p2 == '0':
                return 0    
            else:
                p1 = instance["NODE_COORDS"][p1]
                p2 = instance["NODE_COORDS"][p2]

                # GEOMETRIC DISTANCE - NOT IMPLEMENTED IN PAPER

                # RRR = 6378.388

                # q1 = math.cos(convertToLatLong(p1[1]) - convertToLatLong(p2[1]))
                # q2 = math.cos(convertToLatLong(p1[0]) - convertToLatLong(p2[0]))
                # q3 = math.cos(convertToLatLong(p1[0]) + convertToLatLong(p2[0]))
                # dij = round((RRR*math.acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3))+1.0))

                # CARTESIAN DISTANCE

                dij = math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

                return dij
        
        # Number of locations
        n = len(instance["NODE_COORDS"].keys())+1 #+1 for dummy start

        del_node = instance["DELETE"]

        X = {i:set() for i in range(n)}

        del_arc = [[set() for j in range(n)] for i in range(n)]
        for node in del_node:
            for [i, j] in del_node[node]:
                i = int(i)
                j = int(j)
                del_arc[i][j].add(int(node))
                del_arc[j][i].add(int(node))
                X[i].add(node)
                X[j].add(node)

        del_arc = [[list(j) for j in i] for i in del_arc]
        deleted_edges = set((int(i),int(j)) for k in del_node.values() for [i,j] in k)

        Y = copy.deepcopy(X)
    
        never_deleted_edges = [(i,j) for i in range(1,n) for j in range(1,n) if i != j and (i,j) not in deleted_edges and (j,i) not in deleted_edges]
        never_deleted_set = set([i for (i,j) in never_deleted_edges])

        never_deleted_dict = {i: set() for (i,j) in never_deleted_edges}

        for (i,j) in never_deleted_edges:
            never_deleted_dict[i].add(j)	
            Y[j].add(i)

        # Travel time
        c = [[getDistance(instance,str(i),str(j)) for j in range(n)] for i in range(n)]

        model = dp.Model(maximize=False, float_cost=True)

        customer = model.add_object_type(number=n)

        # U
        unvisited = model.add_set_var(object_type=customer, target=list(range(1, n)))
        # i
        location = model.add_element_var(object_type=customer, target=0)
        # first visited location
        first = model.add_element_var(object_type=customer, target=0)
        # del table
        d = model.add_set_table(del_arc, object_type=customer)

        travel_time = model.add_float_table(c)

        #for adding:
            # instead of deletion dictionary is subset of unvisited
            # visiting any of nodes ADDS that arc
            # so addition_dictionary intersect unvisited < addition_dictionary as at least 1 must be visitied
            # any(unvisited & d[location,j])

        for j in range(1, n):
            visit = dp.Transition(
                name="visit {}".format(j),
                cost=travel_time[location, j] + dp.FloatExpr.state_cost(),
                preconditions=[j != first,location != 0,unvisited.contains(j), unvisited.len()>1, d[location,j].intersection(unvisited).is_empty()],
                effects=[
                    (unvisited, unvisited.remove(j)),
                    (location, j)
                ],
            )
            model.add_transition(visit)

        #TODO: for j in possible_first_nodes
        for j in range(1, n):
            first_visit = dp.Transition(
                name="first visit {}".format(j),
                cost= travel_time[location, j] + dp.FloatExpr.state_cost(),
                preconditions=[location == 0], #, set(range(1,n)) == unvisited
                effects=[
                    (location, j),
                    (first, j) #(unvisited, unvisited.remove(j))
                ],
            )
            model.add_transition(first_visit)

        for j in range(1, n):
            last_visit = dp.Transition(
                name="last visit {}".format(j),
                cost=travel_time[location, j] + dp.FloatExpr.state_cost(),
                effects=[
                    (unvisited, unvisited.remove(j)),
                ],
                preconditions=[d[location,j].intersection(unvisited).is_empty(), unvisited.contains(j), 
                            unvisited.len()==1]
            )
            model.add_transition(last_visit)

        model.add_base_case([unvisited.is_empty()]) #, location == 0, first == 0])

        # # State constraint 
        # for j in range(1,n):
        #     if j not in never_deleted_set: #all edges are deleted
        #         model.add_state_constr(
        #         ~unvisited.contains(j) | ~unvisited.intersection(Y[j]).is_empty() 
        #     )
        # for j in range(1, n):
        #     model.add_state_constr(
        #         ~unvisited.contains(j) | (d[location,j].intersection(unvisited).is_empty())
        #     )

        min_to = model.add_float_table(
            [0] + [min(c[k][j] for k in range(1,n) if k != j) for j in range(1,n)]
        )

        model.add_dual_bound(min_to[unvisited] + (location != 0).if_then_else(min_to[0], 0))

        min_from = model.add_float_table(
            [0] + [min(c[j][k] for k in range(1,n) if k != j) for j in range(1,n)]
        )

        model.add_dual_bound(
            min_from[unvisited] + (location != 0).if_then_else(min_from[location], 0)
        )

        solver = dp.CABS(model, time_limit=tlim)
        solution = solver.search()

        sequence = []

        for t in solution.transitions:
            if t.name != "return":
                sequence.append(t.name.split(" ")[-1])

        sequence = list(reversed(sequence))
        print(sequence)

        #first:
        # sequence = [21,11,29,24,8,14,9,25,35,13,30,12,48,32,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]
        
        #optimal:
        # sequence = [21,30,29,44,37,35,24,5,4,12,51,52,14,27,11,13,25,1,8,39,9,32,23,48,38,22,45,34,7,46,20,36,28,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]

        #12h:
        # sequence = [37,5,46,25,26,13,52,14,29,7,2,20,36,8,32,18,17,31,35,39,38,4,16,50,44,45,40,33,48,27,24,10,6,19,41,22,12,30,42,11,1,9,23,21,34,43,28,47,49,3,15,51]

        #1s:
        # sequence = [21,30,29,11,13,14,12,48,24,35,25,9,32,8,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]

        # sequence = [21,11,29,24,8,14,9,25,35,13,30,12,48,32,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]
        
        # sequence = list(reversed(sequence))
        # sequence = [3, 2, 8, 11, 9, 7, 6, 14, 5, 4, 12, 13, 1, 10]
        # sequence = [str(i) for i in sequence]
        # print([str(int(i)-1) for i in sequence])
        print("ALGORITHM END")

        #check don't go along removed edges
        print("Deletion Check: ", vlad.checkRemovedEdgesDIDP(sequence,del_node))
        print("Length Check: ", vlad.checkLength(sequence,c))
        #viz.tsp_plot(os.path.basename(fpath), sequence, instance["NODE_COORDS"], solution.cost)

        print("Best Bound: {}".format(solution.best_bound))
        print("Cost: {}".format(solution.cost))
        print("Expanded: {}".format(solution.expanded))
        print("Generated: {}".format(solution.generated))
        print("Infeasible: {}".format(solution.is_infeasible))
        print("Optimal: {}".format(solution.is_optimal))
        print("Time: {}".format(solution.time))
        print("Memory Used (MiB): {}".format(round(process.memory_info().rss / 1024 ** 2,2)))
        # print("Transitions: {}".format([int(i.name.split(' ')[-1]) for i in solution.transitions][:-1]))

        print("---RESULTS END")
        

