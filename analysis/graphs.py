import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


with open(r'results\DIDP-results.json', 'r') as f:
    data = json.load(f)

# Closing file
f.close()


# Iterating through the json list

num_instances = len(data)
num_infeasible = 0
num_optimal = 0

algs = set()
instances = set()

for i in data:
    algs.add(data[i]["algorithm"])
    instances.add(data[i]["instance"])

res = {i:{"num_instances":0,"num_infeasible":0,"num_optimal":0} for i in algs}
res_i = {i:{"alg":[],"primal":[],"dual":[],"time":[],"expanded":[],"generated":[]} for i in instances}


for i in data:
    alg = data[i]["algorithm"]
    ins = data[i]["instance"]

    res_i[ins]["alg"].append(alg)
    res_i[ins]["primal"].append(data[i]["best_primal"])
    res_i[ins]["dual"].append(data[i]["best_dual"])
    res_i[ins]["time"].append(data[i]["time"])
    res_i[ins]["expanded"].append(data[i]["expanded"])
    res_i[ins]["generated"].append(data[i]["generated"])
    

    res[alg]["num_instances"] += 1
    if data[i]["optimal"]:
        res[alg]["num_optimal"] += 1
    if data[i]["infeasible"]:
        res[alg]["num_infeasible"] += 1

new_data = {}

allowed_instances = set()

for i in res_i:
    if len(res_i[i]["alg"])>1:
        allowed_instances.add(i)
#         print("===")
#         print(i)
#         print(res_i[i]["alg"])
#         print(res_i[i]["primal"])
#         print(res_i[i]["dual"])
#         print(res_i[i]["time"])
#         print(res_i[i]["expanded"])
#         print(res_i[i]["generated"])

j = 0
for i in data:
    if data[i]["instance"] in allowed_instances:
        new_data[j] = data[i]
        j += 1

res_pd = pd.DataFrame.from_dict(new_data)
res_df = transposed_df = res_pd.transpose()
# print(res_df.columns)

sns.barplot(res_df,x="instance",y="expanded",hue="algorithm")
plt.show()
