import didppy as dp
import math
import json
import os 
import csv
import copy
import validate as vlad
import visualize as viz
import ntpath
import contextlib
import io
from contextlib import contextmanager

import sys
import warnings

import winerror
import win32api
import win32job

g_hjob = None

def create_job(job_name='', breakaway='silent'):
    hjob = win32job.CreateJobObject(None, job_name)
    if breakaway:
        info = win32job.QueryInformationJobObject(hjob,
                    win32job.JobObjectExtendedLimitInformation)
        if breakaway == 'silent':
            info['BasicLimitInformation']['LimitFlags'] |= (
                win32job.JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK)
        else:
            info['BasicLimitInformation']['LimitFlags'] |= (
                win32job.JOB_OBJECT_LIMIT_BREAKAWAY_OK)
        win32job.SetInformationJobObject(hjob,
            win32job.JobObjectExtendedLimitInformation, info)
    return hjob

def assign_job(hjob):
    global g_hjob
    hprocess = win32api.GetCurrentProcess()
    try:
        win32job.AssignProcessToJobObject(hjob, hprocess)
        g_hjob = hjob
    except win32job.error as e:
        if (e.winerror != winerror.ERROR_ACCESS_DENIED or
            sys.getwindowsversion() >= (6, 2) or
            not win32job.IsProcessInJob(hprocess, None)):
            raise
        warnings.warn('The process is already in a job. Nested jobs are not '
            'supported prior to Windows 8.')

def limit_memory(memory_limit):
    if g_hjob is None:
        return
    info = win32job.QueryInformationJobObject(g_hjob,
                win32job.JobObjectExtendedLimitInformation)
    info['ProcessMemoryLimit'] = memory_limit
    info['BasicLimitInformation']['LimitFlags'] |= (
        win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY)
    win32job.SetInformationJobObject(g_hjob,
        win32job.JobObjectExtendedLimitInformation, info)

def main (fpath, outputpath, timelimit):

    # sys.stdout = open(outputpath, 'wt')

    print("===INSTANCE START")
    print("Instance Name: {}".format(ntpath.basename(fpath)))

    assign_job(create_job())
    memory_limit = 8 * 1024 * 1024 * 1024 # 8 GiB
    limit_memory(memory_limit)
    try:
        bytearray(memory_limit)
    except MemoryError:
        print('Success: available memory is limited.')
    else:
        print('Failure: available memory is not limited.')

    with open(fpath, 'r') as file:
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
    # for i in range(n):
    #     for j in range(n):
    #         if len(del_arc[i][j]) == 0:
    #             del_arc[i][j].append(0) #ones that don't need to be added are there from the start

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
    # # t (resource variable)
    # time = model.add_int_resource_var(target=0, less_is_better=True)
    # del table
    d = model.add_set_table(del_arc, object_type=customer)

    travel_time = model.add_float_table(c)

    #for adding:
        # instead of deletion dictionary is subset of unvisited
        # visiting any of nodes ADDS that arc
        # so addition_dictionary intersect unvisited < addition_dictionary as at least 1 must be visitied
        # any(unvisited & d[location,j])

    # print(del_arc[9][11])

    for j in range(1, n):
        visit = dp.Transition(
            name="visit {}".format(j),
            cost=travel_time[location, j] + dp.FloatExpr.state_cost(),
            #del: d[location,j].issubset(unvisited)
            #del ? : d[location,j].difference(unvisited).len() > 0
            #add: d[location,j].intersection(unvisited).len() == 0

            #use is_empty instead of len

            preconditions=[j != first,location != 0,unvisited.contains(j), unvisited.len()>1, d[location,j].intersection(unvisited).is_empty()],
            effects=[
                (unvisited, unvisited.remove(j)),
                (location, j)
            ],
        )
        model.add_transition(visit)

    #TODO: for j in possible_first_nodes
    for j in never_deleted_set:
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

    #TODO: based on dict for first node
    for j in never_deleted_set:
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

    #But what if you create a parameter X_j that contains all the locations that delete edges going to j. 
    # If such a set deletes all edged to j then you know that j \notin U OR X_j \intersect U != \emptyset. 
    # If not all edges to j get deleted by some node, 
    # you might even do better if you add to X_j all the nodes connected to j whose edges never get deleted: 
    # if (i,j) is an edge that never gets deleted and i \in N\U and we're not currently at i, 
    # then effectively (i,j) has been deleted - we can't go back to i so we can't use (i,j).

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
        [min(c[k][j] for k in range(n) if k != j) for j in range(n)]
    )

    

    model.add_dual_bound(min_to[unvisited] + (location != 0).if_then_else(min_to[0], 0))

    min_from = model.add_float_table(
        [min(c[j][k] for k in range(n) if k != j) for j in range(n)]
    )

    model.add_dual_bound(
        min_from[unvisited] + (location != 0).if_then_else(min_from[location], 0)
    )

    solver = dp.CABS(model, time_limit=timelimit)
    solution = solver.search()

    sequence = []

    for t in solution.transitions:
        if t.name != "return":
            sequence.append(t.name.split(" ")[-1])

    sequence = list(reversed(sequence))

    print("ALGORITHM END")

    #check don't go along removed edges
    # print("Deletion Check: ", vlad.checkRemovedEdgesDIDP(sequence,del_node))
    # print("Length Check: ", vlad.checkLength(sequence,c))

    #viz.tsp_plot(os.path.basename(fpath), sequence, instance["NODE_COORDS"], solution.cost)

    print("Best Bound: {}".format(solution.best_bound))
    print("Cost: {}".format(solution.cost))
    print("Expanded: {}".format(solution.expanded))
    print("Generated: {}".format(solution.generated))
    print("Infeasible: {}".format(solution.is_infeasible))
    print("Optimal: {}".format(solution.is_optimal))
    print("Time: {}".format(solution.time))
    print("Transitions: {}".format([int(i.name.split(' ')[-1]) for i in solution.transitions][:-1]))

    print("---RESULTS END")
    

folderpath = os.getcwd()
instance_folder = os.path.join(folderpath,"instances")
tlim = 1800
folderpath = os.getcwd()
instance_folder = os.path.join(folderpath,"instances","ham_bound","random20-50")
tlim = 1800

for instance in os.listdir(instance_folder):
    # if "burma14-3.1.json" == instance:
    fname = os.path.join(instance_folder,instance)
    output_path = os.path.join(folderpath,"log", instance[:-5]+"_"+str(tlim)+".log")
    main(fname, output_path, timelimit = tlim)