import docplex.cp.model as cp
from docplex.cp import config
import math
import json
import os 
import csv
import validate as vlad
import visualize as viz

def main (fpath, opt, export_results = False, trace_log = False):

  if trace_log:
    print(os.path.join(folderpath,"logs","CP",fpath+"_"+opt+"_log.out"))
    stdoutf = open(os.path.join(folderpath,"logs","CP",fpath+"_"+opt+"_log.out"), 'w')
    config.context.log_output = stdoutf
    config.context.solver.trace_log = True

  with open(fpath, 'r') as file:
      instance = json.load(file)

  def convertToLatLong(x):
    deg = round(x)
    minute = x-deg
    lat = (math.pi*(deg+5*minute)/3)/180
    return lat

  def getDistance(instance, p1,p2, end):

    if p1 == '0' or p2 == '0' or p1 == end or p2 == end:
      return 0    
    else:
      p1 = instance["NODE_COORDS"][p1]
      p2 = instance["NODE_COORDS"][p2]

      RRR = 6378.388

      q1 = math.cos(convertToLatLong(p1[1]) - convertToLatLong(p2[1]))
      q2 = math.cos(convertToLatLong(p1[0]) - convertToLatLong(p2[0]))
      q3 = math.cos(convertToLatLong(p1[0]) + convertToLatLong(p2[0]))
      dij = round((RRR*math.acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3))+1.0))
      return dij

  Delete_Dict = instance["DELETE"]

  # Number of locations
  n = len(instance["NODE_COORDS"].keys())
  
  # Travel time
  #w_i,j
  w = [[getDistance(instance,str(i),str(j), str(n+1)) for j in range(n+2)] for i in range(n+2)]

  upper_bound = sum(max(w[i] for i in range(n+2)))

  # Create model
  mdl = cp.CpoModel()

  ## Variables 

  # Node 0 = dummy start
  # Nodes 1 to n= real nodes
  # Node n+1 = dummy end

  traverse = {(i,j) : mdl.interval_var(name='From:{}_To:{}'.format(i,j), optional=True, size=w[i][j], end = (0,upper_bound))
              for i in range(n+1) for j in range(1,n+2) if (i != j and j-i != n+1)}

  enter = { i : mdl.interval_var(name='In:{}'.format(i), end = (0,upper_bound))
          for i in range(1,n+2)}

  out = { i : mdl.interval_var(name='Out:{}'.format(i), end = (0,upper_bound))
          for i in range(n+1)}
  
  def sequence_all():
    sequence_in_out = mdl.sequence_var([i for i in enter.values()] + [i for i in out.values()], name = 'seq_var_in_out')
    #mdl.add(mdl.no_overlap(sequence_in_out))
    return sequence_in_out

  def sequence_ins():
    sequence_in = mdl.sequence_var([i for i in enter.values()], name = 'seq_var_in')
    mdl.add(mdl.no_overlap(sequence_in))
    return sequence_in
  
  def sequence_outs():
    sequence_out = mdl.sequence_var([i for i in out.values()], name = 'seq_var_out')
    mdl.add(mdl.no_overlap(sequence_out))
    return sequence_out

  def sequence_traverses():
    sequence_traverse = mdl.sequence_var([i for i in traverse.values()], name = 'seq_var_traverse')
    mdl.add(mdl.no_overlap(sequence_traverse))
    return sequence_traverse

  def three_sequences():
    sequence_in = sequence_ins()
    sequence_out = sequence_outs()
    sequence_traverse = sequence_traverses()
    mdl.add(mdl.no_overlap(sequence_in))
    mdl.add(mdl.no_overlap(sequence_out))
    mdl.add(mdl.no_overlap(sequence_traverse))
    return sequence_in, sequence_out, sequence_traverse

  if opt == "all":
    sequence_in_out = sequence_all()
    mdl.add(mdl.first(sequence_in_out, out[0]))
    mdl.add(mdl.last(sequence_in_out, enter[n+1]))

  elif opt == "ins":
    sequence_in = sequence_ins()
    for i in range(1,n+2):
     mdl.add(mdl.start_before_start(out[0],enter[i]))
    mdl.add(mdl.last(sequence_in, enter[n+1]))

  elif opt == "outs":
    sequence_out = sequence_outs()
    mdl.add(mdl.first(sequence_out, out[0]))
    for i in range(0,n+1):
      mdl.add(mdl.start_before_start(out[i],enter[n+1]))

  elif opt == "traverses":
    sequence_traverse = sequence_traverses()
    for i in range(1,n+2):
      mdl.add(mdl.start_before_start(out[0],enter[i]))
    for i in range(0,n+1):
      mdl.add(mdl.start_before_start(out[i],enter[n+1]))

  elif opt == "three":
    sequence_in, sequence_out, sequence_traverse = three_sequences()
    mdl.add(mdl.first(sequence_out, out[0]))
    mdl.add(mdl.last(sequence_out, out[n]))
    mdl.add(mdl.first(sequence_in, enter[1]))
    mdl.add(mdl.last(sequence_in, enter[n+1]))

  elif opt == "none":
    pass

  # Out interval starts when Enter interval ends
  mdl.add(mdl.start_at_end(out[i],enter[i]) for i in range(1,n+1))

  # Must use edges j,k before they are deleted by going to node i
  for i in Delete_Dict.keys():
    mdl.add(mdl.end_before_start(traverse[int(j),int(k)],enter[int(i)]) for [j,k] in Delete_Dict[i])

  # Alternatives for enter and out intervals
  mdl.add(mdl.alternative(enter[i], [traverse[j,i] for [j,k] in traverse if k == i]) for i in range(1,n+2))
  mdl.add(mdl.alternative(out[i], [traverse[i,j] for [k,j] in traverse if k == i]) for i in range(n+1))


  # Minimize termination date
  mdl.add(cp.minimize(mdl.end_of(enter[n+1])))

  #mdl.export_model(r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\burma14-3.1.cpo")

  # Solve model
  print('Solving model...')
  #res = mdl.solve()

  solver = cp.CpoSolver(mdl) #, TimeLimit=timelimit, Workers=1)
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

  if export_results:
    print(os.path.join(folderpath,"results","CP",fpath+"_"+opt+".csv"))
    with open(os.path.join(folderpath,"results","CP",fpath+"_"+opt+".csv"), 'w', newline='') as csvfile:
      spamwriter = csv.writer(csvfile, delimiter=',',
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
      for row in range(len(results_over_time["TIME"])):
        spamwriter.writerow([results_over_time["TIME"][row],results_over_time["UB"][row],results_over_time["LB"][row]])

  solution_dict = {"sequence":{},"in":{},"out":{}, "traverse":{}}

  for i in traverse:
    if sol.get_value(traverse[i]) != ():
        solution_dict["sequence"][i[0]] = i[1]
        solution_dict["traverse"][i[0]] = sol.get_value(traverse[i])

  for i in enter:
    if sol.get_value(enter[i]) != ():
      solution_dict["in"][i] = sol.get_value(enter[i])

  for i in out:
    if sol.get_value(out[i]) != ():
      solution_dict["out"][i] = sol.get_value(out[i])

  #checks sequence is valid (all locations visited)
  print("SEQUENCE CHECK: ",vlad.checkSequence(solution_dict["sequence"]))

  #check starting is at 0
  print("START CHECK: ", vlad.checkFirst(solution_dict["in"][solution_dict["sequence"][0]]))

  #check length makes sense
  print("LENGTH CHECK: ", vlad.checkLength(solution_dict["traverse"],solution_dict["in"][n+1]))

  #check don't go along removed edges
  print("DELETION CHECK: ", vlad.checkRemovedEdges(solution_dict["sequence"],Delete_Dict))

  #visualize as job shop
  #viz.tsp_as_jobshop(solver,traverse,14)

  if trace_log:
    stdoutf.close()

folderpath = os.getcwd()
instance = "burma14-3.1"
fname = os.path.join(folderpath,"instances",instance+".json")

#options:
  #all = sequence ins and outs
  #ins = sequence only ins
  #outs = sequence only outs
  #traverses = sequence traverses
  #three = sequence ins, outs,and traverses
  #none = no sequence

opts = ["all","ins","outs","traverses","three","none"]

main(fname, "none", export_results = True, trace_log=True)

for opt in opts:
  print("OPTION: ",opt)
  #main(fname, opt, export_results = True, trace_log=True)