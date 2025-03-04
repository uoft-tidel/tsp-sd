import os
import json

def isfloat(item):

    if item == '0\n':
        return True

    try:
        return float(item)
    except:
        return False

folderpath = os.getcwd()
results_folder = os.path.join(folderpath,"logs")
all_instances = {}
j_val = -1
# instance = "cp-test.txt"

for instance in [f for f in os.listdir(results_folder) if "mip" in f]:
    fname = os.path.join(results_folder, instance)
    instances = {}
    instance_lookup = {}
    print(fname)
    f = open(fname,"r")
    for l in f:
        if "===INSTANCE START" in l:
            j_val += 1
            i_name = l.split(" ")[1][:-6]
            instances[j_val] = {"instance":"","algorithm":"","beam_size":{"size":[],"expanded":[],"time":[]},"dual":{"bound":[],"expanded":[],"time":[]},"primal":{"bound":[],"expanded":[],"time":[]},"hit_time_limit":False,"hit_memory_limit":False,"best_dual":0,"best_primal":0,"expanded":0,"generated":0,"infeasible":True,"optimal":False,"time":0,"transitions":[],"memory":0,"nodes":0}

        elif "ALG:" in l:
            alg_name = l.split(" ")[1][:-1]
            instances[j_val]["algorithm"] = alg_name
        elif "Instance Name:" in l:
            instance_name = l.split(" ")[2][:-6]
            if "random" in instance_name:
                nodes = int(instance_name.split("-")[1])
            else:
                nodes = [s for s in instance_name.split("-")[0] if s.isdigit()]
                nodes = int("".join(nodes))
            instances[j_val]["instance"] = instance_name
            instances[j_val]["nodes"] = nodes
        elif "Memory limit reached" in l:
            instances[j_val]["memory_limit_reached"] = True
        elif "best bound" in l:
            dual = l.split(" ")[5]
            if dual == "-,":
                dual = 0
            else:
                dual = float(dual[:-1])
            instances[j_val]["dual"]["bound"] = dual
        elif "Obj:" in l:
            primal = l.split(" ")[1]
            if primal == "inf":
                primal == 0
            else:
                primal = float(primal)
            instances[j_val]["primal"]["bound"] = primal
        elif "Memory used" in l:
            memused = float(l.split(" ")[-1])
            instances[j_val]["memory"] = memused
        elif "Time:" in l:
            timeused = float(l.split(" ")[-1])
            instances[j_val]["time"] = timeused

    all_instances.update(instances)

print(instances)

# with open('DIDP-results.json','w') as res:
#     json.dump(all_instances,res)