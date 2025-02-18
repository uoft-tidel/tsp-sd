import os
import json

folderpath = os.getcwd()
results_folder = os.path.join(folderpath,"results")
all_instances = {}
i_val = 0

for instance in os.listdir(results_folder):
    fname = os.path.join(results_folder, instance)
    instances = {}
    instance_lookup = {}
    print(fname)
    f = open(fname,"r")
    j_val = 0
    for l in f:
        if "Instance Name" in l:
            i_name = l.split(" ")[2][:-6]
            instance_lookup[j_val] = i_val #in order
            instances[i_val] = {"instance":"","algorithm":"","beam_size":{"size":[],"expanded":[],"time":[]},"dual":{"bound":[],"expanded":[],"time":[]},"primal":{"bound":[],"expanded":[],"time":[]},"hit_time_limit":False,"best_dual":0,"best_primal":0,"expanded":0,"generated":0,"infeasible":True,"optimal":False,"time":0,"transitions":[]}
            i_val += 1
            j_val += 1

    f.seek(0)

    i = -1
    j = -1
    for l in f:
        if "Solver:" in l:
            i += 1
            i_name = instance_lookup[i]
        elif "===INSTANCE START" in l:
            j += 1
            j_name = instance_lookup[j]
        elif "Searched" in l:
            beam_size = int(l.split(" ")[4][:-1])
            expanded = int(l.split(" ")[6][:-1])
            elapsed_time = float(l.split(" ")[9].strip())
            instances[i_name]["beam_size"]["size"].append(beam_size)
            instances[i_name]["beam_size"]["expanded"].append(expanded)
            instances[i_name]["beam_size"]["time"].append(elapsed_time)
        elif "New dual" in l:
            bound = float(l.split(" ")[3][:-1])
            expanded = int(l.split(" ")[5][:-1])
            elapsed_time = float(l.split(" ")[8].strip())
            instances[i_name]["dual"]["bound"].append(bound)
            instances[i_name]["dual"]["expanded"].append(expanded)
            instances[i_name]["dual"]["time"].append(elapsed_time)
        elif "New primal" in l:
            bound = float(l.split(" ")[3][:-1])
            expanded = int(l.split(" ")[5][:-1])
            elapsed_time = float(l.split(" ")[8].strip())
            instances[i_name]["primal"]["bound"].append(bound)
            instances[i_name]["primal"]["expanded"].append(expanded)
            instances[i_name]["primal"]["time"].append(elapsed_time)
        elif "Reached time" in l:
            instances[i_name]["hit_time_limit"] = True
        elif "ALG:" in l:
            instances[j_name]["algorithm"] = l.split(" ")[-1].strip()
        elif "Instance Name:" in l:
            instances[j_name]["instance"] = l.split(" ")[-1].strip()[:-5]
        elif "Best Bound" in l:
            if 'None' in l:
                instances[j_name]["best_dual"] = 0
            else:
                instances[j_name]["best_dual"] = float(l.split(" ")[-1].strip())
        elif "Cost:" in l:
            if 'None' in l:
                instances[j_name]["best_primal"] = 0
            else:
                instances[j_name]["best_primal"] = float(l.split(" ")[-1].strip())
        elif "Expanded:" in l:
            instances[j_name]["expanded"] = int(l.split(" ")[-1].strip())
        elif "Generated:" in l:
            instances[j_name]["generated"] = int(l.split(" ")[-1].strip())
        elif "Infeasible:" in l:
            if "False" in l:
                instances[j_name]["infeasible"] = False
            else:
                instances[j_name]["infeasible"] = True
        elif "Optimal:" in l:
            if "False" in l:
                instances[j_name]["optimal"] = False
            else:
                instances[j_name]["optimal"] = True
        elif "Time:" in l:
            instances[j_name]["time"] = float(l.split(" ")[-1].strip())
        elif "Transitions:" in l: 
            instances[j_name]["transitions"] = json.loads(l[13:].strip())
    all_instances.update(instances)

with open('DIDP-results.json','w') as res:
    json.dump(all_instances,res)