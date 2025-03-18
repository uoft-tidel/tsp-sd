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

    # script, timelim, batch = sys.argv
    # timelim = "1800"
    # batch = "1"
    folderpath = os.getcwd()
    instance_folder = os.path.join(folderpath,"instances","selected")
    # instance_folder = os.path.join(folderpath,"instances","selected_and_quintiles",batch)
    tlim = 1800

<<<<<<< HEAD
    for instance in [f for f in os.listdir(instance_folder) if "rat" in f]:
=======
    for instance in [f for f in os.listdir(instance_folder) if "berlin52-10.4" in f]:
>>>>>>> parent of 24bdd69 (no first changes, sbatch)
        print(instance)
        # if "burma14-3.1.json" == instance:
        fname = os.path.join(instance_folder, instance)
        # output_path = os.path.join(folderpath,"log", instance[:-5]+"_"+str(tlim)+".log")

        print("===INSTANCE START")
        print("ALG: DIDP-ADD")
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

        solver = dp.CABS(model, time_limit=tlim)
        # solution = solver.search()

        sequence = []

        # for t in solution.transitions:
        #     if t.name != "return":
        #         sequence.append(t.name.split(" ")[-1])

        # sequence = list(reversed(sequence))

        #first:
        # sequence = [21,11,29,24,8,14,9,25,35,13,30,12,48,32,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]
        
        #optimal:
        # sequence = [21,30,29,44,37,35,24,5,4,12,51,52,14,27,11,13,25,1,8,39,9,32,23,48,38,22,45,34,7,46,20,36,28,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]

        #12h:
        # sequence = [37,5,46,25,26,13,52,14,29,7,2,20,36,8,32,18,17,31,35,39,38,4,16,50,44,45,40,33,48,27,24,10,6,19,41,22,12,30,42,11,1,9,23,21,34,43,28,47,49,3,15,51]

        #1s:
        # sequence = [21,30,29,11,13,14,12,48,24,35,25,9,32,8,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]

        # sequence = [21,11,29,24,8,14,9,25,35,13,30,12,48,32,27,45,34,51,37,28,36,20,1,38,23,39,22,52,4,44,46,7,5,43,41,50,2,26,6,42,47,49,3,19,18,15,17,40,33,31,10,16]
<<<<<<< HEAD
        sequence = [305,28,73,175,284,317,353,609,782,562,670,720,744,633,376,96,116,187,283,473,588,684,737,747,781,774,379,397,574,620,616,352,429,177,108,78,70,153,183,161,239,260,513,415,681,732,775,757,585,641,605,293,9,106,4,14,40,147,65,39,139,127,151,102,98,8,109,452,659,544,521,590,344,308,347,182,129,145,124,134,548,762,619,564,591,654,255,395,213,89,13,94,110,235,511,572,460,638,559,555,365,735,731,666,729,722,741,662,524,453,190,445,311,275,658,750,601,592,653,623,613,717,611,432,371,289,93,114,367,278,676,663,649,699,671,608,606,417,372,170,333,749,640,454,425,312,492,502,550,576,292,296,506,470,706,392,496,273,112,27,26,38,57,7,332,253,427,314,713,674,725,778,773,738,627,634,726,715,533,194,184,19,52,221,265,396,420,450,165,34,285,391,553,345,144,85,125,81,74,33,59,86,236,385,593,509,583,602,612,346,667,539,516,522,503,665,388,160,97,21,72,118,141,196,240,369,561,507,597,645,686,579,501,639,497,304,214,133,130,390,248,206,172,541,596,498,476,30,200,79,69,32,326,472,510,229,779,772,719,765,756,698,648,655,437,462,250,166,259,505,680,760,547,279,142,20,61,119,216,400,554,411,446,247,512,325,49,54,154,568,693,708,727,673,700,566,746,734,685,675,754,586,482,343,252,204,451,257,268,491,64,43,201,37,12,323,191,269,351,272,117,136,104,338,375,742,764,647,552,569,714,743,723,381,274,45,126,16,99,80,410,267,423,242,18,534,316,107,143,88,162,302,328,399,374,493,543,584,349,386,3,105,25,111,53,148,100,336,480,237,761,466,626,241,294,188,15,71,207,67,60,545,594,661,752,540,441,44,82,17,231,205,664,651,538,486,186,354,748,668,630,682,621,439,402,405,246,322,546,361,198,642,652,694,683,499,382,753,408,430,303,287,270,414,360,475,628,771,679,705,422,444,434,689,703,299,56,22,58,222,68,95,251,558,488,551,514,226,48,156,263,220,152,589,578,618,389,483,168,128,87,428,528,629,556,500,209,244,573,733,494,565,199,307,208,149,171,174,313,582,542,393,418,36,435,595,449,140,0,215,469,300,421,701,290,47,29,46,146,243,90,50,487,377,687,691,777,768,696,179,238,234,363,137,291,517,672,702,770,615,77,181,508,531,520,406,364,657,580,755,739,660,712,656,357,176,426,122,11,342,527,769,758,692,598,416,409,763,624,622,728,646,378,306,261,625,245,455,677,337,123,91,266,84,355,24,457,51,193,359,532,232,233,407,335,366,277,567,256,63,219,227,228,650,443,523,66,189,178,394,6,62,438,465,471,536,324,436,535,401,398,614,173,525,587,339,115,318,518,519,348,632,495,707,581,489,478,477,463,383,327,309,281,180,83,132,334,164,113,103,264,202,474,636,515,604,440,92,42,225,467,319,464,603,736,710,711,751,724,709,329,35,76,310,563,424,644,607,767,766,716,249,211,461,759,730,704,295,138,637,678,560,412,286,330,413,600,121,203,75,212,223,101,120,158,456,740,447,610,577,484,404,745,163,1,341,135,150,254,280,276,575,282,195,288,230,131,224,301,549,537,167,458,695,643,721,635,297,298,776,599,358,331,210,197,481,468,362,448,271,373,570,504,368,169,529,442,697,688,485,490,159,155,370,23,157,55,10,41,387,192,218,433,356,258,262,526,479,571,557,384,459,530,315,431,780,718,669,380,31,2,185,403,631,690,340,617,419,350,5,320,217,321]

=======
        
>>>>>>> parent of 24bdd69 (no first changes, sbatch)
        sequence = list(reversed(sequence))
        sequence = [str(i) for i in sequence]

        print("ALGORITHM END")

        #check don't go along removed edges
        print("Deletion Check: ", vlad.checkRemovedEdgesDIDP(sequence,del_node))
        print("Length Check: ", vlad.checkLength(sequence,c))

        #viz.tsp_plot(os.path.basename(fpath), sequence, instance["NODE_COORDS"], solution.cost)

        # print("Best Bound: {}".format(solution.best_bound))
        # print("Cost: {}".format(solution.cost))
        # print("Expanded: {}".format(solution.expanded))
        # print("Generated: {}".format(solution.generated))
        # print("Infeasible: {}".format(solution.is_infeasible))
        # print("Optimal: {}".format(solution.is_optimal))
        # print("Time: {}".format(solution.time))
        # print("Memory Used (MiB): {}".format(round(process.memory_info().rss / 1024 ** 2,2)))
        # print("Transitions: {}".format([int(i.name.split(' ')[-1]) for i in solution.transitions][:-1]))

        print("---RESULTS END")
        

