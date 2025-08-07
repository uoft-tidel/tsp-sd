import json
import csv
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import font_manager
import json

import matplotlib.patheffects as pe
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
import pandas as pd

with open(r'results\original\merged-original-results.json', 'r') as f:
    data = json.load(f)

with open(r'results\no_first_last\merged-original-nofirst_last-results.json', 'r') as f2:
    data_nof = json.load(f2)

# Closing file
f.close()
f2.close()

res = {"DIDP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "DIDP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-RANK-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-RANK-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "MIP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "MIP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]}}

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


i_best_nof = {}
feasible_nof = {}

res_nof = {"DIDP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "DIDP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-RANK-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "CP-RANK-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "MIP-ADD":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]},
       "MIP-DEL":{"times":[],"gaps":[],"updated_gaps":[],"average_gap":[]}}

unique_times_nof = set()

for i in data_nof:
    instance = data_nof[i]["instance"].split(".json")[0]
    if "random" in instance:
      alg = data_nof[i]["algorithm"]
      if alg == "DIDP-ADD":
        if data_nof[i]["best_primal"] > 0:
          i_best_nof[instance] = data_nof[i]["best_primal"]
          feasible_nof[instance] = True
        else:
          feasible_nof[instance] = False

for i in data_nof:
    instance = data_nof[i]["instance"].split(".json")[0]
    if "random" in instance and feasible_nof[instance]:
      alg = data_nof[i]["algorithm"]
      primal = data_nof[i]["primal"]["bound"]
      if primal != []:
        best = i_best_nof[instance]
        time = data_nof[i]["primal"]["time"]
        gap = [(i - best)/i for i in primal]
      elif data_nof[i]["best_primal"] > 0:
        best = i_best_nof[instance]
        gap = [1, (data_nof[i]["best_primal"]-best)/data_nof[i]["best_primal"]]
        time = [0, data_nof[i]["time"]]
      else:
         gap = [1,1]
         time = [0,1800]

      # if alg == "DIDP-DEL":
      #   print(instance, gap[-1])

      unique_times_nof = unique_times_nof.union(set(time))
      res_nof[alg]["times"].append(time)
      res_nof[alg]["gaps"].append(gap)
      
times = sorted(list(unique_times))

times_nof = sorted(list(unique_times_nof))

def find_nearest_small_index(key, sorted_li):
    try:
      return max(ind for ind, i in enumerate(sorted_li) if i <= key)
    except:
      return -1

for alg in res_nof:
  print(alg)
  for i in range(39):
    res_nof[alg]["updated_gaps"].append([])
    if i < len(res_nof[alg]["gaps"]):
      for t in times_nof:
        ind_i = find_nearest_small_index(t,res_nof[alg]["times"][i])
        if ind_i == -1:
          res_nof[alg]["updated_gaps"][-1].append(1)
        else:  
          res_nof[alg]["updated_gaps"][-1].append(res_nof[alg]["gaps"][i][ind_i])
    else:
      for t in times_nof:
        res_nof[alg]["updated_gaps"][-1].append(1)

for alg in res_nof:
  for t_ind,t in enumerate(times_nof):
    gaps = [res_nof[alg]["updated_gaps"][i][t_ind] for i in range(39)]
    res_nof[alg]["average_gap"].append(sum(gaps)/39)

res_df_dict_nof = {alg_convert[alg]: res_nof[alg]["average_gap"] for alg in res_nof}
res_df_dict_nof["Time (s)"] = times_nof

res_df_dict = {alg_convert[alg]: res[alg]["average_gap"] for alg in res}
res_df_dict["Time (s)"] = times

# print(res_df_dict)

##GRAPH 1 - PRIMAL OVER TIME

graph_df = pd.DataFrame.from_dict(res_df_dict)

graph_df_nof = pd.DataFrame.from_dict(res_df_dict_nof)
# font_path = r"C:\Users\Daniel\Downloads\lm\lm\fonts\opentype\public\lm\lmroman12-bold.otf"  # Your font path goes here
# font_manager.fontManager.addfont(font_path)
# prop = font_manager.FontProperties(fname=font_path)

sns.set_theme(style="ticks")

# Define the palette as a list to specify exact values
palette = sns.color_palette("husl", 9)

cols1 = ["DIDP Add", "CP Rank Add", "CP Rank Del", "MIP Del", "MIP Add", "CP Interval Del", "CP Interval Add","DIDP Del"]
cols = ["MIP Del", "MIP Add", "DIDP Del", "CP Interval Del", "CP Rank Add", "CP Rank Del", "CP Interval Add", "DIDP Add"]


cols2 = ["DIDP", "CP Rank", "MIP", "CP Interval"]

clrs = sns.color_palette("hls", 4)
colours = {}

for i,clr in enumerate(clrs):
   colours[cols2[i]] = clr


# graph_df.to_csv("res_overtime.csv",sep=',')
# graph_df_nof.to_csv("res_overtime_nof.csv",sep=',')

# Plot the lines on two facets
fig, axs = plt.subplots(figsize=(13, 5),ncols=2)
# ax.yaxis.set_major_formatter(ticker.EngFormatter())
for i,each in enumerate(cols):
    if "Add" in each:
      ls = '-'
    else:
      ls = '--'
    sns.lineplot(data = graph_df, x = 'Time (s)', y = each, label = str(each), color=colours[each[:-4]], linestyle=ls, linewidth=2.5, ax=axs[0], path_effects=[pe.Stroke(linewidth=3.5, foreground='white',alpha=1), pe.Normal()])
    sns.lineplot(data = graph_df_nof, x = 'Time (s)', y = each, label = str(each), color=colours[each[:-4]], linestyle=ls, linewidth=2.5,ax=axs[1], path_effects=[pe.Stroke(linewidth=3.5, foreground='white',alpha=1), pe.Normal()])

sns.despine()

fig.suptitle('Primal Gap Over Time', fontsize=18) # or plt.suptitle('Main title')
axs[0].set_xlim(0,1800)
axs[0].set_ylim(0,1)
# axs[1].ylim(0,60)
axs[0].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

axs[0].axes.grid(visible=True)
axs[0].axes.set_title("With First/Last Vertex Restrictions", fontsize=16)
axs[0].axes.tick_params(axis='both', labelsize=14)
axs[0].axes.set(xlabel='Time (s)', ylabel='Primal Gap')
axs[0].axes.xaxis.label.set_size(16)
axs[0].axes.yaxis.set_major_locator(ticker.MultipleLocator(0.2))
axs[0].axes.yaxis.label.set(fontsize='16')
axs[0].get_legend().set_visible(False)
# sns.move_legend(axs[0], "upper left", bbox_to_anchor=(1, 1))
# plt.setp(axs[0].get_legend().get_texts(), fontsize='14') # 

axs[1].set_xlim(0,1800)
axs[1].set_ylim(0,1)
# axs[1].ylim(0,60)
axs[1].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

axs[1].set_title("Without First/Last Vertex Restrictions", fontsize=16)
axs[1].tick_params(axis='both', labelsize=14)
axs[1].set(xlabel='Time (s)', ylabel='')
axs[1].xaxis.label.set_size(16)
axs[1].yaxis.set_major_locator(ticker.MultipleLocator(0.2))
axs[1].yaxis.label.set(fontsize='16')
sns.move_legend(axs[1], "upper left", bbox_to_anchor=(1, 1))
plt.setp(axs[1].get_legend().get_texts(), fontsize='14') # 

plt.show()

    
     
     

      # res.append([instance, alg] + primal)
      # res.append([instance, alg] + time)




# with open('primals_over_time2.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(res)

