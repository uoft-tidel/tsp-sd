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
results_folder = os.path.join(folderpath,"logs","original")
all_instances = {}
j = 1999
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
            j += 1
            i_name = l.split(" ")[1][:-6]
            instances[j] = {"instance":"","algorithm":"","dual":{"bound":[],"expanded":[],"time":[]},"primal":{"bound":[],"gap":[],"time":[]},"hit_time_limit":False,"hit_memory_limit":False,"best_dual":0,"best_primal":0,"explored":0,"iterations":0,"infeasible":False,"optimal":False,"time":0,"transitions":[],"memory":0,"nodes":0}

            cont = False
            empty_counter = 0

        if "Instance Name: " in l:
            instances[j]["instance"] = l.split(" ")[-1].strip()
        elif "ALG:" in l:
            alg_name = l.split(" ")[1][:-1]
            if alg_name == "MIP-ADD-2":
                alg_name = "MIP-ADD"
            instances[j]["algorithm"] = alg_name
        # elif "Optimize a model with" in l:
        #     line = l.strip().split(" ")
        #     instances[j]["original_rows"] = int(line[4])
        #     instances[j]["original_cols"] = int(line[6])
        #     instances[j]["original_nonzeros"] = int(line[9])

        # elif "Variable types: " in l:
        #     line = l.strip().split(" ")
        #     if instances[j]["original_bin_vars"] == 0:
        #       instances[j]["original_cont_vars"] = int(line[2])
        #       instances[j]["original_int_vars"] = int(line[4])
        #       instances[j]["original_bin_vars"] = int(line[6][1:])
        #     else:
        #       instances[j]["num_cont_vars"] = int(line[2])
        #       instances[j]["num_int_vars"] = int(line[4])
        #       instances[j]["num_bin_vars"] = int(line[6][1:]) 


        # elif "Presolve removed" in l:
        #     line = l.split(" ")
        #     instances[j]["presolve_remove_rows"] = int(line[2])
        #     instances[j]["presolve_remove_cols"] = int(line[5])

        # elif "Presolve time" in l:
        #     line = l.split(" ")
        #     instances[j]["presolve_time"] = float(line[-1][:-2])

        # elif "Presolved: " in l:
        #     line = l.split(" ")
        #     instances[j]["presolved_rows"] = int(line[1])
        #     instances[j]["presolved_cols"] = int(line[3])
        #     instances[j]["presolved_nonzeros"] = int(line[5])

        elif "Expl Unexpl" in l:
            cont = True

        elif cont:

            if l == '\n':
                empty_counter += 1
                if empty_counter == 2:
                    cont = False
            elif 'Explored' in l or 'Cutting' in l:
                cont = False
            elif 'infeasible' in l or 'cutoff' in l:
                pass
            else:
                line = [i for i in l.split(" ") if i != '']
                time = float(line[-1].strip()[:-1])
                try:
                    gap_index = b = [y for y,x in enumerate(line) if "%" in x][0]
                    new_gap = float(line[gap_index][:-1])
                    new_dual = float(line[gap_index-1])
                    new_primal = float(line[gap_index-2])
                    instances[j]["primal"]["bound"].append(new_primal)
                    instances[j]["primal"]["time"].append(time)
                    instances[j]["dual"]["bound"].append(new_dual)
                    instances[j]["dual"]["time"].append(time)     
                    instances[j]["gap"]["gap"].append(new_gap)
                    instances[j]["gap"]["time"].append(time)
                except:
                    new_dual = float(line[-4])
                    instances[j]["dual"]["bound"].append(new_dual)
                    instances[j]["dual"]["time"].append(time)     
                
        elif "Time limit reached" in l:
            instances[j]["hit_time_limit"] = True
        elif "Memory limit reached" in l:
            instances[j]["hit_memory_limit"] = True
        elif "Model is infeasible" in l:
            instances[j]["infeasible"] = True
        elif "Memory Used" in l:
            instances[j]["memory"] = float(l.split(" ")[-1].strip())
        elif "Explored" in l:
            line = l.split(" ")
            explored = int(line[1])
            iterations = int(line[3][1:])
            instances[j]["explored"] = explored
            instances[j]["iterations"] = iterations

        elif "Optimal" in l:
            instances[j]["optimal"] = True
        elif "Memory limit reached" in l:
            instances[j]["memory_limit_reached"] = True
        elif "best bound" in l:
            dual = l.split(" ")[5]
            if dual == "-,":
                dual = 0
            else:
                dual = float(dual[:-1])
            instances[j]["best_dual"] = dual
            instances[j]["best_gap"] = l.split(" ")[-1].strip()[:-1] 
        elif "Obj:" in l:
            primal = l.split(" ")[1]
            if primal == "inf":
                primal == 0
            else:
                primal = float(primal)
            
            if math.isinf(primal):
                primal = 0
            instances[j]["best_primal"] = primal
        elif "Groups: " in l:
            instances[j]["num_groups"] = int(l.split(" ")[-1].strip())
        elif "Time:" in l:
            timeused = float(l.split(" ")[-1])
            instances[j]["time"] = timeused
        elif "Grouped elements" in l:
            groups = eval(l.split("Grouped elements:  ")[-1])
            instances[j]["groups"] = groups
        elif "Element sections" in l:
            sections = eval(l.split("Element sections:  ")[-1])
            instances[j]["sections"] = sections

    all_instances.update(instances)

results_fname = os.path.join(folderpath,"results","MIP-results-OG-time.json")

with open(results_fname,'w') as res:
    json.dump(all_instances,res)