import docplex.cp.model as cp
import math
import json

def main (fpath, opt):

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

  enter = { i : mdl.interval_var(name='In:{}'.format(i))
          for i in range(1,n+2)}

  out = { i : mdl.interval_var(name='Out:{}'.format(i))
          for i in range(n+1)}
  
  def sequence_all():
    sequence_in_out = mdl.sequence_var([i for i in enter.values()] + [i for i in out.values()], name = 'seq_var_in_out')
    mdl.add(mdl.no_overlap(sequence_in_out))
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
    return sequence_in, sequence_out, sequence_traverse

  if opt == "all":
    sequence_in_out = sequence_all()
    mdl.add(mdl.first(sequence_in_out, out[0]))
    mdl.add(mdl.last(sequence_in_out, enter[n+1]))

  elif opt == "ins":
    sequence_in = sequence_ins()
    mdl.add(mdl.first(sequence_in, enter[1]))
    mdl.add(mdl.last(sequence_in, enter[n+1]))

  elif opt == "outs":
    sequence_out = sequence_outs()
    mdl.add(mdl.first(sequence_out, out[0]))
    mdl.add(mdl.last(sequence_out, out[n]))

  elif opt == "traverses":
    sequence_traverse = sequence_traverses()
    # TODO: Set out[0] to be first, enter[n+1] to be last

  elif opt == "three":
    sequence_in, sequence_out, sequence_traverse = three_sequences()
    mdl.add(mdl.first(sequence_out, out[0]))
    mdl.add(mdl.last(sequence_out, out[n]))
    mdl.add(mdl.first(sequence_in, enter[1]))
    mdl.add(mdl.last(sequence_in, enter[n+1]))

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


  #-----------------------------------------------------------------------------
  # Solve the model 
  #-----------------------------------------------------------------------------

  #mdl.export_model(r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\burma14-3.1.cpo")

  # Solve model
  print('Solving model...')
  res = mdl.solve()
  print('Solution:')
  res.print_solution()


main(r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\burma14-3.1.json", "all")