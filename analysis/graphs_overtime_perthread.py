import json
import csv
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import font_manager
import json

from matplotlib.ticker import MaxNLocator
import pandas as pd

with open(r'results\merged-results-threads.json', 'r') as f:
    data = json.load(f)

# Closing file
f.close()

set_algs = "DIDP Add, DIDP Del, CP Rank Add, CP Rank Del"
res = {i:{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[], ""} for i in set_algs}

i_best = {}
feasible = {}

for i in data:
    instance = data[i]["instance"].split(".json")[0]
    if "random" in instance:
      alg = data[i]["algorithm"]
      if alg == "DIDP-ADD":
        if data[i]["best_primal"] > 0:
          i_best[instance] = data[i]["best_primal"]
          feasible[instance] = True
        else:
          feasible[instance] = False

unique_times = set()

for i in data:
    instance = data[i]["instance"].split(".json")[0]
    if "random" in instance and feasible[instance]:
      alg = data[i]["algorithm"]
      primal = data[i]["primal"]["bound"]
      if primal != []:
        best = i_best[instance]
        time = data[i]["primal"]["time"]
        gap = [(i - best)/i for i in primal]
      elif data[i]["best_primal"] > 0:
        best = i_best[instance]
        gap = [1, (data[i]["best_primal"]-best)/data[i]["best_primal"]]
        time = [0, data[i]["time"]]
      else:
         gap = [1,1]
         time = [0,1800]

      if alg == "DIDP-DEL":
        print(instance, gap[-1])

      unique_times = unique_times.union(set(time))
      res[alg]["times"].append(time)
      res[alg]["gaps"].append(gap)
      
times = sorted(list(unique_times))

def find_nearest_small_index(key, sorted_li):
    try:
      return max(ind for ind, i in enumerate(sorted_li) if i <= key)
    except:
      return -1

for alg in res:
  print(alg)
  for i in range(39):
    res[alg]["updated_gaps"].append([])
    if i < len(res[alg]["gaps"]):
      for t in times:
        ind_i = find_nearest_small_index(t,res[alg]["times"][i])
        if ind_i == -1:
          res[alg]["updated_gaps"][-1].append(1)
        else:  
          res[alg]["updated_gaps"][-1].append(res[alg]["gaps"][i][ind_i])
    else:
      for t in times:
        res[alg]["updated_gaps"][-1].append(1)

alg_convert = {"DIDP-ADD": "DIDP Add", 
               "DIDP-DEL": "DIDP Del", 
               "CP-ADD": "CP Interval Add", 
               "CP-DEL": "CP Interval Del", 
               "MIP-ADD": "MIP Add", 
               "MIP-DEL": "MIP Del", 
               "CP-RANK-ADD": "CP Rank Add", 
               "CP-RANK-DEL": "CP Rank Del", }

for alg in res:
  for t_ind,t in enumerate(times):
    gaps = [res[alg]["updated_gaps"][i][t_ind] for i in range(39)]
    res[alg]["average_gap"].append(sum(gaps)/39)



res_df_dict = {alg_convert[alg]: res[alg]["average_gap"] for alg in res}
res_df_dict["Time (s)"] = times

# print(res_df_dict)

##GRAPH 1 - PRIMAL OVER TIME

graph_df = pd.DataFrame.from_dict(res_df_dict)

# font_path = r"C:\Users\Daniel\Downloads\lm\lm\fonts\opentype\public\lm\lmroman12-bold.otf"  # Your font path goes here
# font_manager.fontManager.addfont(font_path)
# prop = font_manager.FontProperties(fname=font_path)

sns.set_theme(style="ticks")

# Define the palette as a list to specify exact values
palette = sns.color_palette("husl", 9)

cols1 = ["DIDP Add", "CP Rank Add", "CP Rank Del", "MIP Del", "MIP Add", "CP Interval Del", "CP Interval Add","DIDP Del"]
cols = ["MIP Add", "MIP Del", "DIDP Del", "CP Interval Add", "CP Rank Add", "CP Rank Del", "CP Interval Del", "DIDP Add"]

clrs = sns.color_palette("hls", 8)
colours = {}

for i,clr in enumerate(clrs):
   colours[cols1[i]] = clr

# Plot the lines on two facets
fig, ax = plt.subplots(figsize=(8, 6.27))
# ax.yaxis.set_major_formatter(ticker.EngFormatter())
for i,each in enumerate(cols):
    sns.lineplot(data = graph_df, x = 'Time (s)', y = each, label = str(each), color=colours[each], linewidth=2.5)

plt.xlim(0,1800)
plt.ylim(0,1.0)
sns.despine()
plt.grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 
ax.set_title("Mean Primal Gap Over Time", fontsize=16)
ax.tick_params(axis='both', labelsize=12)
ax.set(xlabel='Time (s)', ylabel='Primal Gap')
ax.xaxis.label.set_size(14)
ax.yaxis.label.set(fontsize='14')
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
plt.setp(ax.get_legend().get_texts(), fontsize='12') # for legend text
# plt.setp(ax.get_legend().get_title(), fontsize='32') # for legend title
# plt.rcParams['font.family'] = 'Latin Modern Roman Bold'
# plt.rcParams['font.sans-serif'] = prop.get_name()
# plt.rcParams.update({'font.size': 30, 'axes.titlesize': 40, 'axes.labelsize': 30})


plt.show()

    
     
     

      # res.append([instance, alg] + primal)
      # res.append([instance, alg] + time)




# with open('primals_over_time2.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(res)

