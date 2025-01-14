import didppy as dp
import math
import json
import os 
import csv
import validate as vlad
import visualize as viz

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
    print("INSTANCE: ", fpath)

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

    del_arc = [[set() for j in range(n)] for i in range(n)]
    for node in del_node:
        for [i, j] in del_node[node]:
            i = int(i)
            j = int(j)
            del_arc[i][j].add(int(node))
            del_arc[j][i].add(int(node))

    del_arc = [[list(j) for j in i] for i in del_arc]

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

            preconditions=[unvisited.contains(j), unvisited.len()>1, d[location,j].intersection(unvisited).is_empty(), first != 0],
            effects=[
                (unvisited, unvisited.remove(j)),
                (location, j)
            ],
        )
        model.add_transition(visit)

    for j in range(1, n):
        first_visit = dp.Transition(
            name="first visit {}".format(j),
            cost= travel_time[location, j] + dp.FloatExpr.state_cost(),
            preconditions=[location == 0, first == 0], #, set(range(1,n)) == unvisited
            effects=[
                (unvisited, unvisited.remove(j)),
                (location, j),
                (first, j)
            ],
        )
        model.add_transition(first_visit)

    for j in range(1,n):
        last_visit = dp.Transition(
            name="last visit {}".format(j),
            cost=travel_time[location, j] + travel_time[j, first] + dp.FloatExpr.state_cost(),
            effects=[
                (unvisited, unvisited.remove(j)),
            ],
            preconditions=[d[first,j].is_empty(), 
                           d[location,j].intersection(unvisited).is_empty(), unvisited.contains(j), 
                           unvisited.len()==1, location != 0]
        )
        model.add_transition(last_visit)

    # return_to_depot = dp.Transition(
    #     name="return",
    #     cost=dp.FloatExpr.state_cost(),
    #     effects=[
    #         (location, 0),
    #         (first, 0)
    #     ],
    #     preconditions=[unvisited.is_empty(), location != 0]
    # )
    # model.add_transition(return_to_depot)

    model.add_base_case([unvisited.is_empty()]) #, location == 0, first == 0])

    #

    # State constraint 
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

    print("Transitions to apply:")

    sequence = []

    for t in solution.transitions:
        print(t.name)
        if t.name != "return":
            sequence.append(t.name.split(" ")[-1])

    sequence = list(reversed(sequence))
    
    #PAPER SOLUTION FOR BERLIN52-10.4:
    #sequence = ['21', '30', '29', '44', '37', '35', '24', '5', '4', '12', '51', '52', '14', '27', '11', '13', '25', '1', '8', '39', '9', '32', '23', '48', '38', '22', '45', '34', '7', '46', '20', '36', '28', '43', '41', '50', '2', '26', '6', '42', '47', '49', '3', '19', '18', '15', '17', '40', '33', '31', '10', '16']
    
    #MIP
    sequence = ["2", "8", "11", "3", "14", "9", "7", "6", "4", "12", "13", "1", "10", "5"]

    #DIDP
    #sequence = ["2", "8", "11", "3", "14", "7", "6", "4", "12", "13", "1", "10", "5", "9"]

    # print(sequence)


    #check don't go along removed edges
    print("DELETION CHECK: ", vlad.checkRemovedEdgesDIDP(sequence,del_node))
    print(vlad.checkLength(sequence,c))
    print(not(solution.is_infeasible))

    #viz.tsp_plot(os.path.basename(fpath), sequence, instance["NODE_COORDS"], solution.cost)

    print("Cost: {}".format(solution.cost))

folderpath = os.getcwd()
#instance = "ulysses22-5.5"
instance_folder = os.path.join(folderpath,"instances")



for instance in os.listdir(instance_folder):
    #if "berlin52-10.4.json" != instance:
    if "burma14-3.1.json" == instance:
        print("hi")
        fname = os.path.join(folderpath,"instances",instance)
        output_path = os.path.join(folderpath,"output", instance[:-5]+"_log.out")
        main(fname, "none", timelimit = 1800)