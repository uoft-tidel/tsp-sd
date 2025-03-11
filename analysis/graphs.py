import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib import font_manager


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

res_per_alg = {i:{"num_instances":0,"num_feasible_found":0,"num_optimal":0,"ind":0, "rand_time_of_proof":[],"proved_over_time_time":[],"proved_over_time_solved":[]} for i in algs}
res_i = {i:{"instance":"","alg":"","nodes":0,"first_primal":0,"ttfs":0,"first_primal_gap":0,"primal":0,"dual":0,"time":0,"mem":0,"primal_integral":0,"expanded/fails/iters":0,"generated/branches/nodes":0} for i in data}
res_per_inst = {i:{"best_primal":0} for i in instances}

for j,i in enumerate(res_per_alg.keys()):
    res_per_alg[i]["ind"] = j

for i in data.keys():

    alg = data[i]["algorithm"]
    res_i[i]["alg"] = alg
    inst = data[i]["instance"]
    res_i[i]["instance"] = inst
    res_i[i]["primal"] = data[i]["best_primal"]
    res_i[i]["dual"] = data[i]["best_dual"]
    res_i[i]["time"] = data[i]["time"]

    

    if "MIP" in alg:
        res_i[i]["expanded/fails/iters"] = data[i]["iterations"]
        res_i[i]["generated/branches/nodes"] = data[i]["explored"]
    elif "CP" in alg:
        res_i[i]["expanded/fails/iters"] = data[i]["fails"]
        res_i[i]["generated/branches/nodes"] = data[i]["branches"]
    else:
        res_i[i]["expanded/fails/iters"] = data[i]["expanded"]
        res_i[i]["generated/branches/nodes"] = data[i]["generated"]

    res_i[i]["nodes"] = data[i]["nodes"]

    if (data[i]["optimal"] or data[i]["infeasible"]) and "random" in inst:
        res_per_alg[alg]["rand_time_of_proof"].append(data[i]["time"])
    

    res_per_alg[alg]["num_instances"] += 1
    if data[i]["optimal"]:
        res_per_alg[alg]["num_optimal"] += 1
    # if data[i]["infeasible"]:
    #     res_per_alg[alg]["num_infeasible"] += 1
    if data[i]["best_primal"] > 0:
        res_per_alg[alg]["num_feasible_found"] += 1

    if res_per_inst[inst]["best_primal"] == 0 or (data[i]["best_primal"] > 0 and data[i]["best_primal"] < res_per_inst[inst]["best_primal"]):
        res_per_inst[inst]["best_primal"] = data[i]["best_primal"]

#get primal gaps over time

for i in data.keys():
    inst = data[i]["instance"]
    best_primal = res_per_inst[inst]["best_primal"]

    if best_primal == 0 or data[i]["primal"]["bound"] == []:
        res_i[i]["primal_intergal"] = -1
    else:
        primal_integral = 0
        time_old = 0

        first_primal_list = [i for i, val in enumerate(data[i]["primal"]["bound"]) if val != 0]
        if first_primal_list != []:
            first_primal_ind = first_primal_list[0]
            res_i[i]["first_primal"] = data[i]["primal"]["bound"][first_primal_ind]
            res_i[i]["ttfs"] = data[i]["primal"]["time"][first_primal_ind]
            res_i[i]["first_primal_gap"] = abs(data[i]["primal"]["bound"][first_primal_ind] - best_primal)/best_primal

        #[0,0,0,0,4,5,6]
        #[1,2,3,4,5,6,7]

        for ind, j in enumerate(data[i]["primal"]["bound"]):
            gap = abs(j - best_primal)/best_primal
            data[i]["primal"]["gap"].append(gap)
            time_new = data[i]["primal"]["time"][ind]
            time_diff = time_new - time_old
            primal_integral += gap * time_diff
            time_old = time_new

        if data[i]["primal"]["bound"][-1] != best_primal and time_old < 1800:
            data[i]["primal"]["time"].append(1800)
            gap = abs(j - best_primal)/best_primal
            data[i]["primal"]["gap"].append(gap)
            time_diff = 1800 - time_old
            primal_integral += gap * time_diff

        res_i[i]["primal_intergal"] = primal_integral/1800
        

res_inst_df = pd.DataFrame.from_dict(res_per_inst).transpose()


new_data = {}

for i in res_per_alg:
    time_vec = sorted(list(set(j for j in res_per_alg[i]["rand_time_of_proof"])))
    amt_vec = [sum(k <= h for k in res_per_alg[i]["rand_time_of_proof"]) for h in time_vec]
    time_vec.append(1800)
    amt_vec.append(amt_vec[-1])
    res_per_alg[i]["proved_over_time_time"] = time_vec
    res_per_alg[i]["proved_over_time_solved"] = amt_vec

res_pd = pd.DataFrame.from_dict(res_i)
res_df = res_pd.transpose()
# print(res_df)

res_alg_pd = pd.DataFrame.from_dict(res_per_alg,)
res_alg_df = res_alg_pd.transpose()
res_alg_df = res_alg_df.reset_index().set_index('ind')

# print(res_per_alg)

# 
# print(res_alg_df)
# print(res_df)


# res_df["best_primal"] = res_df[res_df["primal"] > 0].groupby(["instance"])["primal"].transform("min")
# res_df["primal_gap"] = (res_df["primal"] - res_df["best_primal"]) / res_df["best_primal"]


# res_df = res_df.sort_values(['nodes'])
# sns.barplot(res_df,x="instance",y="primal_integral",hue="alg")


# res_df = res_df.sort_values(['nodes'])

order = []
for i in range(len(algs)):
    order.append((res_alg_df.iloc[i, 0],i))

order.sort(key=lambda tup: tup[0])
for (i,ind) in order:
    plt.plot(res_alg_df.iloc[ind, 5], res_alg_df.iloc[ind, 6], label=res_alg_df.iloc[ind, 0])

# sns.barplot(res_df,x="alg",y="primal",hue="nodes")

# res_alg_df = res_alg_df.sort_values(['num_optimal'])
# sns.barplot(res_alg_df,x="index",y="num_optimal")

# res_alg_df = res_alg_df.sort_values(['num_feasible_found'])
# sns.barplot(res_alg_df,x="index",y="num_feasible_found")


font_path = r"C:\Users\Daniel\Downloads\lm\lm\fonts\opentype\public\lm\lmroman12-regular.otf"  # Your font path goes here
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

plt.rcParams['font.family'] = 'Latin Modern Roman'
plt.rcParams['font.sans-serif'] = prop.get_name()

# print([f.name for f in matplotlib.font_manager.fontManager.ttflist])

# res_df.to_csv("res5.csv",sep=',')

plt.rcParams["font.family"] = "Latin Modern Roman"
plt.title("Instances Proven Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Instances Proven (Optimal or Infeasible)")
plt.legend(["CP Interval Add", "CP Interval Del", "CP Rank Add", "CP Rank Del", "DIDP Add", "DIDP Del", "MIP Add", "MIP Del"],bbox_to_anchor=(0.6, 0.9), loc='upper left', borderaxespad=0)

plt.show()

