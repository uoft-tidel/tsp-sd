import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


with open(r'results\merged-results.json', 'r') as f:
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

res_per_alg = {i:{"num_instances":0,"num_feasible_found":0,"num_infeasible":0,"num_optimal":0,"ind":0} for i in algs}
res_i = {i:{"instance":"","alg":"","nodes":0,"primal":0,"dual":0,"time":0,"mem":0,"expanded":0,"generated":0} for i in data}

for j,i in enumerate(res_per_alg.keys()):
    res_per_alg[i]["ind"] = j

for i in data.keys():

    alg = data[i]["algorithm"]
    res_i[i]["alg"] = alg
    res_i[i]["instance"] = data[i]["instance"]
    res_i[i]["primal"] = data[i]["best_primal"]
    res_i[i]["dual"] = data[i]["best_dual"]
    res_i[i]["time"] = data[i]["time"]
    # res_i[i]["expanded"] = data[i]["expanded"]
    # res_i[i]["generated"] = data[i]["generated"]
    res_i[i]["nodes"] = data[i]["nodes"]
    

    res_per_alg[alg]["num_instances"] += 1
    if data[i]["optimal"]:
        res_per_alg[alg]["num_optimal"] += 1
    if data[i]["infeasible"]:
        res_per_alg[alg]["num_infeasible"] += 1
    if data[i]["best_primal"] > 0:
        res_per_alg[alg]["num_feasible_found"] += 1

new_data = {}

res_pd = pd.DataFrame.from_dict(res_i)
res_df = res_pd.transpose()

res_alg_pd = pd.DataFrame.from_dict(res_per_alg,)
res_alg_df = res_alg_pd.transpose()
res_alg_df = res_alg_df.reset_index().set_index('ind')

print(res_alg_df)


res_df["best_primal"] = res_df[res_df["primal"] > 0].groupby(["instance"])["primal"].transform("min")
res_df["primal_gap"] = (res_df["primal"] - res_df["best_primal"]) / res_df["best_primal"]

# print(res_df["primal_gap"])

# res_df = res_df.sort_values(['nodes'])
# sns.lineplot(res_df[res_df["nodes"] <= 200],x="nodes",y="time",hue="alg")

# sns.barplot(res_df,x="alg",y="primal",hue="nodes")

# res_alg_df = res_alg_df.sort_values(['num_optimal'])
# sns.barplot(res_alg_df,x="index",y="num_optimal")

# res_alg_df = res_alg_df.sort_values(['num_feasible_found'])
# sns.barplot(res_alg_df,x="index",y="num_feasible_found")


plt.show()

