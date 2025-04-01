import os
import json
import csv

folderpath = os.getcwd()
results_folder = os.path.join(folderpath,"logs","permutator","1_thread_20_cpu")
all_instances = {}
i_val = 0

header = ["instance","num","feasible","fitness"]
res = []

for instance in [f for f in os.listdir(results_folder) if "berlin52-10.4" not in f]:


    fname = os.path.join(results_folder, instance)
    with open(fname,'r+') as file:
           # First we load existing data into a dict.
        data = json.load(file)

    i_name = instance
    print(i_name)
    num = instance.split("-")[0]
    feasible = data["solution"]["is_feasible"]
    fitness = data["solution"]["fitness"]

    res_row = [i_name, num, feasible, fitness]
    res.append(res_row)

with open('our_perm_1thread_20cpu-all.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(res)


# results_fname = os.path.join(folderpath,"results","perm-results.json")
