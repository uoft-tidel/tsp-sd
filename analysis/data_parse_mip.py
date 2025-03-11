import os
import json
import math

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
j_val = 1999
# instance = "cp-test.txt"

for instance in [f for f in os.listdir(results_folder) if "MIP" in f]:
    fname = os.path.join(results_folder, instance)
    instances = {}
    instance_lookup = {}
    f = open(fname,"r")
    print(fname)
    
    cont = False
    for l in f:
        if "===INSTANCE START" in l:
            j_val += 1
            i_name = l.split(" ")[1][:-6]
            instances[j_val] = {"instance":"","algorithm":"","dual":{"bound":[],"expanded":[],"time":[]},"primal":{"bound":[],"gap":[],"time":[]},"hit_time_limit":False,"hit_memory_limit":False,"best_dual":0,"best_primal":0,"explored":0,"iterations":0,"infeasible":False,"optimal":False,"time":0,"transitions":[],"memory":0,"nodes":0}

            cont = False
            empty_counter = 0

        elif cont:

            if l == '\n':
                empty_counter += 1
                if empty_counter == 2:
                    cont = False
            else:
                line = [i for i in l.split(" ") if i != '']
                time = float(line[-1].strip()[:-1])
                if 'H' in l:
                    new_primal = float(line[2])
                    new_dual = float(line[3])
                elif '*' in l:
                    new_primal = float(line[3])
                    new_dual = float(line[4])
                elif "cutoff" in l or "infeasible" in l:
                    if line[4] == "-":
                        new_primal = 0
                    else:
                        new_primal = float(line[4])
                    if line[5] == "infeasible":
                        new_dual = 0
                    else:
                        new_dual = float(line[5])
                else:
                    if line[5] == "-":
                        new_primal = 0
                    else:
                        new_primal = float(line[5])
                    if line[6] == "-":
                        new_dual = 0
                    else:
                        new_dual = float(line[6])
                instances[j_val]["primal"]["bound"].append(new_primal)
                instances[j_val]["primal"]["time"].append(time)
                instances[j_val]["dual"]["bound"].append(new_dual)
                instances[j_val]["dual"]["time"].append(time)


        elif "Expl Unexpl" in l:
            cont = True

       

        elif "ALG:" in l:
            alg_name = l.split(" ")[1][:-1]
            if alg_name == "MIP-ADD-2":
                alg_name = "MIP-ADD"
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
        elif "Model is infeasible" in l:
            instances[j_val]["infeasible"] = True
        elif "Explored" in l:
            line = l.split(" ")
            explored = int(line[1])
            iterations = int(line[3][1:])
            instances[j_val]["explored"] = explored
            instances[j_val]["iterations"] = iterations

        elif "Optimal" in l:
            instances[j_val]["optimal"] = True
        elif "Memory limit reached" in l:
            instances[j_val]["memory_limit_reached"] = True
        elif "best bound" in l:
            dual = l.split(" ")[5]
            if dual == "-,":
                dual = 0
            else:
                dual = float(dual[:-1])
            instances[j_val]["best_dual"] = dual
        elif "Obj:" in l:
            primal = l.split(" ")[1]
            if primal == "inf":
                primal == 0
            else:
                primal = float(primal)
            
            if math.isinf(primal):
                primal = 0
            instances[j_val]["best_primal"] = primal
        elif "Memory used" in l:
            memused = float(l.split(" ")[-1])
            instances[j_val]["memory"] = memused
        elif "Time:" in l:
            timeused = float(l.split(" ")[-1])
            instances[j_val]["time"] = timeused

    all_instances.update(instances)

results_fname = os.path.join(folderpath,"results","MIP-results.json")

with open(results_fname,'w') as res:
    json.dump(all_instances,res)