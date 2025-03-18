import os
import json

import re

def isfloat(item):

    if item == '0\n':
        return True

    try:
        return float(item)
    except:
        return False

folderpath = os.getcwd()
results_folder = os.path.join(folderpath,"logs","original")
all_instances = {}
j_val = 999
# instance = "cp-test.txt"

for instance in [f for f in os.listdir(results_folder) if "CP" in f]:
    fname = os.path.join(results_folder, instance)
    instances = {}
    instance_lookup = {}
    print(fname)
    f = open(fname,"r")
    cont = False
    
    time = 0
    for l in f:

        if cont:
            if "Search terminated" in l:
                cont = False

            elif "Search completed" in l:
                cont = False
            
            elif "New bound" in l:
                new_bound = float(l.split(" ")[5].strip())
                instances[j_val]["dual"]["bound"].append(new_bound)
                instances[j_val]["dual"]["time"].append(time)

            elif "*" in l:
                new_primal = float([i for i in l.split(" ") if i != '' and i != '*'][0])
                time = float([i for i in l.split(" ") if "s" in i][0][:-1])
                instances[j_val]["primal"]["bound"].append(new_primal)
                instances[j_val]["primal"]["time"].append(time)


        if "===INSTANCE" in l:
            j_val += 1
            i_name = l.split(" ")[1][:-6]
            instances[j_val] = {"instance":"","algorithm":"","dual":{"bound":[],"expanded":[],"time":[]},"primal":{"bound":[],"gap":[],"time":[]},"hit_time_limit":False,"best_dual":0,"best_primal":0,"branches":0,"fails":0,"infeasible":False,"optimal":False,"time":0,"transitions":[],"memory":0,"nodes":0}

        elif "model has no solution" in l:
            instances[j_val]["infeasible"] = True

        elif "Initial process time" in l:
            time = float(l.split(" ")[6][:-1])
        elif "Using sequential search" in l:
            cont = True

        elif "ALG:" in l:
            alg_name = l.split(" ")[1][:-1]
            instances[j_val]["algorithm"] = alg_name
            if "rank" in alg_name:
                obj_mult = 0.1
            else:
                obj_mult = 1
        elif "Instance Name:" in l:
            instance_name = l.split(" ")[2][:-6]
            if "random" in instance_name:
                nodes = int(instance_name.split("-")[1])
            else:
                nodes = [s for s in instance_name.split("-")[0] if s.isdigit()]
                nodes = int("".join(nodes))
            instances[j_val]["instance"] = instance_name
            instances[j_val]["nodes"] = nodes
        elif "Best objective" in l:
            primal = l.split(" ")
            primal = [float(s) for s in primal if isfloat(s)][0]*obj_mult
            instances[j_val]["best_primal"] = primal
            if "optimal" in l:
                instances[j_val]["optimal"] = True

        elif "Best bound" in l:
            dual = l.split(" ")
            dual = [float(s) for s in dual if isfloat(s)][0]*obj_mult
            instances[j_val]["best_dual"] = dual
        elif "Number of branches" in l:
            num_branches = int(l.split(" ")[-1].strip())
            instances[j_val]["branches"] = num_branches
            print(num_branches)

        elif "Number of fails" in l:
            num_fails = int(l.split(" ")[-1].strip())
            instances[j_val]["fails"] = num_fails
            print(num_fails)
        elif "Total memory usage" in l:
            if "GB" in l:
                mem_mult = 1000
            else:
                mem_mult = 1
            memused = l.split(" ")
            memused = [float(s) for s in memused if isfloat(s)][0]*mem_mult
            instances[j_val]["memory"] = memused
        elif "Time spent in solve" in l:
            timeused = l.split(" ")
            timeused = [float(s[:-1]) for s in timeused if isfloat(s[:-1])]
            if timeused == []:
                timeused = 0
            else:
                timeused = timeused[0]
            instances[j_val]["time"] = timeused

    all_instances.update(instances)

results_fname = os.path.join(folderpath,"results","CP-results_OG.json")

with open(results_fname,'w') as res:
    json.dump(all_instances,res)