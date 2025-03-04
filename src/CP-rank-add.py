#! /usr/bin/env python3

import docplex.cp.model as cp
from docplex.cp import config
import math
import json
import os 
import os 
import sys
# import validate as vlad
# import visualize as viz

if __name__ == "__main__":

  script, timelim, batch = sys.argv
  folderpath = os.getcwd()
  instance_folder = os.path.join(folderpath,"instances",batch)
  # instance_folder = r"C:\Users\pekar\Documents\Github\TSP-SD\instances\1"
  tlim = int(timelim)


  for instance in os.listdir(instance_folder):
    fname = os.path.join(instance_folder,instance)
    # output_path = os.path.join(folderpath,"log", instance[:-5]+"_"+str(tlim)+".log")

    print("===INSTANCE START")
    print("ALG: CP-RANK-ADD")
    print("Instance Name: {}".format(os.path.basename(fname)))

    with open(fname, 'r') as file:
        instance = json.load(file)

    def convertToLatLong(x):
      deg = round(x)
      minute = x-deg
      lat = (math.pi*(deg+5*minute)/3)/180
      return lat

    def getDistance(instance, p1,p2):

      p1 = instance["NODE_COORDS"][p1]
      p2 = instance["NODE_COORDS"][p2]

      # RRR = 6378.388

      # q1 = math.cos(convertToLatLong(p1[1]) - convertToLatLong(p2[1]))
      # q2 = math.cos(convertToLatLong(p1[0]) - convertToLatLong(p2[0]))
      # q3 = math.cos(convertToLatLong(p1[0]) + convertToLatLong(p2[0]))
      # dij = round((RRR*math.acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3))+1.0))

      dij = math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

      return dij

    Delete_Dict = instance["DELETE"]

    # Number of locations
    n = len(instance["NODE_COORDS"].keys())

    deleted_edges = set((int(i),int(j)) for k in Delete_Dict.values() for [i,j] in k)
    
    never_deleted_edges = [(i,j) for i in range(1,n+1) for j in range(1,n+1) if i != j and (i,j) not in deleted_edges and (j,i) not in deleted_edges]
    never_deleted_set = set([i for (i,j) in never_deleted_edges])

    never_deleted_dict = {i: set() for (i,j) in never_deleted_edges}
    for (i,j) in never_deleted_edges:
      never_deleted_dict[i].add(j)			

    # Travel time
    #w_i,j
    w = [[getDistance(instance,str(i),str(j)) for j in range(1,n+1)] for i in range(1,n+1)]
    max_dist = int(max([max(i) for i in w]))
    print(max_dist)

    #upper_bound = sum(max(w[i] for i in range(n+1)))

    # Create model
    mdl = cp.CpoModel()

    ## Variables 
    node = [mdl.integer_var(name="Node at Rank 0",domain = [i-1 for i in never_deleted_set])]
    node += [mdl.integer_var(name=f"Node at Rank {i}",domain = [i for i in range(n)]) for i in range(1,n-1)]
    node += [mdl.integer_var(name=f"Node at Rank {n-1}",domain = [i-1 for i in never_deleted_set])]
    rank = []
    for i in range(n):
      if i+1 in never_deleted_set:
        rank += [mdl.integer_var(name=f"Rank of Node {i}",domain = [i for i in range(n)])]
      else:
        rank += [mdl.integer_var(name=f"Rank of Node {i}",domain = [i for i in range(1,n-1)])]

    ## Constraints
    mdl.add(mdl.inverse(rank,node))
    mdl.add(mdl.all_diff(rank))
    mdl.add(mdl.all_diff(node))

    #either:
      # RANK J->K ISNT 1 APART
      # or 
      # RANK J <= rank i AND rank k <= rank i 

    for i in Delete_Dict.keys():
      for [j,k] in Delete_Dict[i]:

        #DELETION
        # mdl.add(mdl.logical_or(mdl.abs(rank[int(j)-1]-rank[int(k)-1])!=1,mdl.logical_and(rank[int(j)-1]<=rank[int(i)-1],rank[int(k)-1]<=rank[int(i)-1])))
        
        #ADDITION
        mdl.add(mdl.logical_or(mdl.abs(rank[int(j)-1]-rank[int(k)-1])!=1,mdl.logical_and(rank[int(j)-1]>=rank[int(i)-1],rank[int(k)-1]>=rank[int(i)-1])))


    for i in never_deleted_dict:
      #need to do i-1, j-1 for 1 index to 0 index
      mdl.add(mdl.if_then(rank[i-1] == 0, mdl.allowed_assignments(node[n-1],[j-1 for j in never_deleted_dict[i]])))
      mdl.add(mdl.if_then(rank[i-1] == n-1, mdl.allowed_assignments(node[0],[j-1 for j in never_deleted_dict[i]])))

    #TODO: WRONG
    #w[i][j] = distance from i to j
    #0-indexed

    mdl.add(cp.minimize(mdl.sum(mdl.element(w[i], mdl.element(node,mdl.mod(mdl.element(rank,i)+1,n))) for i in range(n))))

    # os.remove("cp_r.cpo")
    # mdl.export_model(r"cp_r.cpo")

    # Solve model
    print('Solving model...')
    #res = mdl.solve()

    solver = cp.CpoSolver(mdl, TimeLimit=tlim, Workers=1)
    results_over_time = {"UB":[],"LB":[],"TIME":[]}

    is_solution_optimal = False
    sol_status = ''
    
    while not is_solution_optimal and sol_status != 'Ended':
      sol = solver.search_next()
      
      if sol.get_solve_status() == 'Unknown' or sol.fail_status == 'SearchCompleted':
        # Solved timed out and could not find a feasible solution
        solver.end_search()
        sol_status = 'Ended'

      results_over_time["UB"].append(sol.get_objective_value())
      results_over_time["LB"].append(sol.get_objective_bounds())
      results_over_time["TIME"].append(sol.get_solve_time())

      is_solution_optimal = sol.is_solution_optimal()

    # if export_results:
    #   print(os.path.join(folderpath,"results","CP",fpath+"_"+opt+".csv"))
    #   with open(os.path.join(folderpath,"results","CP",fpath+"_"+opt+".csv"), 'w', newline='') as csvfile:
    #     spamwriter = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     for row in range(len(results_over_time["TIME"])):
    #       spamwriter.writerow([results_over_time["TIME"][row],results_over_time["UB"][row],results_over_time["LB"][row]])

    solution_dict = {"sequence":{},"in":{},"out":{}, "traverse":{}, "seq_list":[]}

    for i in range(len(node)):
      print(f"Rank {i} : Node {sol.get_value(node[i])}")

    # os.remove(r"C:\Users\pekar\Documents\GitHub\tsp-sd\cp-rank-soln")
    # sol.write("cp-rank-soln")


    # for i in traverse:
    #   if sol.get_value(traverse[i]) != ():
    #       solution_dict["sequence"][i[0]] = i[1]
    #       solution_dict["traverse"][i[0]] = sol.get_value(traverse[i])

    # for i in traverse_last:
    #   if sol.get_value(traverse_last[i]) != ():
    #       solution_dict["sequence"][i[0]] = n+1
    #       solution_dict["traverse"][i[0]] = sol.get_value(traverse_last[i])


    # for i in enter:
    #   if sol.get_value(enter[i]) != ():
    #     solution_dict["in"][i] = sol.get_value(enter[i])

    # for i in out:
    #   if sol.get_value(out[i]) != ():
    #     solution_dict["out"][i] = sol.get_value(out[i])

    # j = 0
    # for i in range(n):
    #   j = solution_dict["sequence"][j]
    #   solution_dict["seq_list"].append(j)

    # print(solution_dict["seq_list"])

    # #checks sequence is valid (all locations visited)
    # print(solution_dict["sequence"])
    # #print("SEQUENCE CHECK: ",vlad.checkSequence(solution_dict["sequence"]))

    # #check starting is at 0
    # print("START CHECK: ", vlad.checkFirst(solution_dict["in"][solution_dict["sequence"][0]]))

    # #check length makes sense
    # print("LENGTH CHECK: ", vlad.checkLength(solution_dict["seq_list"],w))

    # #check don't go along removed edges
    # print("DELETION CHECK: ", vlad.checkRemovedEdgesCP(solution_dict["sequence"],Delete_Dict))

    #visualize as job shop
    #viz.tsp_as_jobshop(solver,traverse,14)

    # if trace_log:
    #   stdoutf.close()

  # folderpath = os.getcwd()
  # ulysses = "ulysses22-5.5"
  # burma = "burma14-3.1"
  # vm = "vm1084-848.9"
  # toy = "toy"
  # instance = vm
  # fname = os.path.join(folderpath,"instances","selected_and_quintiles","1",instance+".json")

  #options:
    #all = sequence ins and outs
    #ins = sequence only ins
    #outs = sequence only outs
    #traverses = sequence traverses
    #three = sequence ins, outs,and traverses
    #none = no sequence

  # opts = ["all","ins","outs","traverses","three","none"]

  # main(fname, "ins", export_results = False, trace_log=False)

  # for opt in opts:
  #   print("OPTION: ",opt)
    #main(fname, opt, export_results = True, trace_log=True)def main (fpath, opt, export_results = False, trace_log = False):

  #   if trace_log:
  #     print(os.path.join(folderpath,"logs","CP",fpath+"_"+opt+"_log.out"))
  #     stdoutf = open(os.path.join(folderpath,"logs","CP",fpath+"_"+opt+"_log.out"), 'w')
  #     config.context.log_output = stdoutf
  #     config.context.solver.trace_log = True

  #   with open(fpath, 'r') as file:
  #       instance = json.load(file)