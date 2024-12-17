import json, math
import gurobipy as gp
from gurobipy import GRB


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

    nodes = [str(i) for i in range(1,len(instance["NODE_COORDS"])+1)]
    n = len(nodes)
    times = [int(t+1) for t in range(n)]
    dist_dict = {(i,j,t): getDistance(instance["NODE_COORDS"][i],instance["NODE_COORDS"][j]) for i in instance["NODE_COORDS"].keys() for j in instance["NODE_COORDS"].keys() for t in times if i != j}
    
    #for i in instance["NODE_COORDS"].keys():
    #    dist_dict[(0,i,0)] = 0
    #    dist_dict[(i,n+1,n+1)] = 0
        
    #times = [0] + times + [n+1]

    del_dict = instance["DELETE"]
    
    return dist_dict, del_dict, nodes, times

def main(fpath):

    distances, deletes, nodes, times = read_file(fpath)

    print(distances)

    #try:
    # Create a new model
    m = gp.Model("TSP-SD")
    n = 14

    # Create variables
    x = m.addVars(distances.keys(), obj = distances, vtype = GRB.BINARY, name="x")

    # m.addConstr(gp.quicksum(x[0, int(j),0] for j in nodes) == 1)
    # m.addConstr(gp.quicksum(x[int(j), n+1,n+1] for j in nodes) == 1)

    for t in times:
        for i in nodes:
            m.addConstr(gp.quicksum(t*x[i, j,t] for j in nodes if i != j) == 1 + gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j))

        m.addConstr(gp.quicksum(x[i, j,t] for i in nodes for j in nodes if i != j) == 1)

    #m.write(r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\test3_2.lp")

    #delete edges (edges can only be visited before they're deleted)
    for (i, dels) in deletes.items():
        #if int(i) <= 12:
        for [n1, n2] in dels:
            m.addConstr(gp.quicksum(t*x[n1, n2,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j))
            m.addConstr(gp.quicksum(t*x[n2, n1,t] for t in times) <= gp.quicksum(t*x[j, i,t] for t in times for j in nodes if i != j))

    # Optimize model
    m.optimize()

    for v in m.getVars():
        if v.X > 0.9:
            print(f"{v.VarName}") #{v.X:g}")

    print(f"Obj: {m.ObjVal:g}")
    print(f"Time: {m.Runtime:g}")

    # except gp.GurobiError as e:
    #     print(f"Error code {e.errno}: {e}")

    # except AttributeError:
    #     print("Encountered an attribute error")

fpath = r"C:\Users\pekar\OneDrive - University of Toronto\Masters\Masters\Code\TSP-ED\burma14-3.1.json"
main(fpath)
