import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import font_manager
import json

import matplotlib.ticker as ticker

import matplotlib.patheffects as pe
from matplotlib.ticker import MaxNLocator
import pandas as pd

##GRAPH 1 - PROVEN OVER TIME - FEASIBLE

with open(r'results\original\merged-original-results.json', 'r') as f:
    data = json.load(f)

with open(r'results\no_first_last\merged-original-nofirst_last-results.json', 'r') as f2:
    data_nof = json.load(f2)

# Closing file
f.close()
f2.close()

best_per_instance = {}

res = {"Proven Optimal or Infeasible": {"CP-RANK-ADD": {10:5, 20:3, 30:3, 40:2, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "CP-ADD": {10:5, 20:5, 30:3, 40:2, 50:2, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "DIDP-ADD": {10:5, 20:5, 30:5, 40:3, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "MIP-ADD": {10:5, 20:3, 30:2, 40:2, 50:1, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "CP-RANK-DEL": {10:5, 20:3, 30:3, 40:2, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "CP-DEL": {10:5, 20:5, 30:3, 40:2, 50:1, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "DIDP-DEL": {10:5, 20:2, 30:1, 40:1, 50:0, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "MIP-DEL": {10:5, 20:3, 30:2, 40:2, 50:2, 60:0, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}},
       "Final Optimal Gap": {"CP-RANK-ADD": {10:5.00022494236906E-05, 20:0.523905745728148, 30:0.317913545528652, 40:0.820553885631354, 50:0.851793790076559, 60:0.954388624567819, 70:0.920369561223472, 80:0.972768879691677, 90:0.956236203022502, 100:0.989170308294669, 150:1, 200:1}, "CP-ADD": {10:0, 20:0, 30:0.389234917719766, 40:0.636256403616931, 50:0.71424700567179, 60:0.911190440485004, 70:0.910884353741497, 80:0.939185760619088, 90:0.968830204687666, 100:0.967938035041369, 150:0.988539743115257, 200:1}, "DIDP-ADD": {10:0, 20:0, 30:0, 40:0.148328950637241, 50:0.191209256400639, 60:0.30605325107712, 70:0.4014079178336, 80:0.411875536302276, 90:0.421584478060484, 100:0.49541235183874, 150:0.565130615616502, 200:0.636165406689883}, "MIP-ADD": {10:-1.05066870421693E-06, 20:0.11296351934004, 30:1, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}, "CP-RANK-DEL": {10:5.00022494236906E-05, 20:0.468357536905915, 30:0.580646337556519, 40:0.723179096008792, 50:0.828910386483509, 60:0.840308818503944, 70:0.985192804048365, 80:0.72901826302984, 90:0.80563197048246, 100:0.999359638929255, 150:1, 200:1}, "CP-DEL": {10:0, 20:0, 30:0.394251891926234, 40:0.831621281036486, 50:0.982038721716818, 60:0.989488437281009, 70:1, 80:1, 90:1, 100:1, 150:0.991207183783823, 200:1}, "DIDP-DEL": {10:0, 20:0.223982920023465, 30:0.65214491025029, 40:0.863192532645712, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:0.926934108594099, 200:1}, "MIP-DEL": {10:-1.05066870421693E-06, 20:0.103758929669344, 30:0.714021153302297, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}},
       "Final Primal Gap":{"CP-RANK-ADD": {10:0.0030448224911316, 20:0.00151338161677183, 30:0.100159323838174, 40:0.173173570056543, 50:0.243831379225545, 60:0.309049975901342, 70:0.402429320319992, 80:0.425568010669714, 90:0.43914256220806, 100:0.489956430005445, 150:0.586374773117583, 200:0.654555708585571}, "CP-ADD": {10:0.00303508342312338, 20:0, 30:0.0339505422396792, 40:0.0520550730896976, 50:0.097028506164681, 60:0.122505152302397, 70:0.129527950603315, 80:0.267425020192711, 90:0.577130916051249, 100:0.407680062916688, 150:0.528074065362067, 200:1}, "DIDP-ADD": {10:0.00304502945390473, 20:0.00151346609794534, 30:0.000241710228659356, 40:0, 50:0, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "MIP-ADD": {10:0.00304398110964756, 20:0.0282717447714471, 30:1, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}, "CP-RANK-DEL": {10:0.0030448224911316, 20:0.00151338161677183, 30:0.078617248393792, 40:0.18595363182265, 50:0.263476983050094, 60:0.322644731881691, 70:0.400015794231963, 80:0.407342119901071, 90:0.429616945621963, 100:0.476105860362766, 150:0.590120875187214, 200:0.637082010660777}, "CP-DEL": {10:0.000023035230352298, 20:0, 30:0.0189995186604488, 40:0.420265115725871, 50:0.77846479429505, 60:0.872476493526885, 70:1, 80:1, 90:1, 100:1, 150:0.656996995778009, 200:1}, "DIDP-DEL": {10:0.00304502945390473, 20:0.00151346609794534, 30:0.385801793422016, 40:0.72560825519164, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:0.838522039759706, 200:1}, "MIP-DEL": {10:0.00304398110964756, 20:0.0236568796875904, 30:0.676581753372461, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}}}

res_nof = {"Proven Optimal or Infeasible": {"CP-RANK-ADD": {10:5, 20:3, 30:3, 40:2, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "CP-ADD": {10:5, 20:5, 30:3, 40:1, 50:0, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "DIDP-ADD": {10:5, 20:5, 30:5, 40:3, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "MIP-ADD": {10:4, 20:5, 30:1, 40:1, 50:0, 60:2, 70:2, 80:2, 90:1, 100:1, 150:0, 200:0}, "CP-RANK-DEL": {10:5, 20:3, 30:3, 40:2, 50:2, 60:2, 70:2, 80:2, 90:1, 100:1, 150:1, 200:1}, "CP-DEL": {10:5, 20:2, 30:0, 40:0, 50:0, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "DIDP-DEL": {10:5, 20:2, 30:1, 40:0, 50:0, 60:0, 70:0, 80:0, 90:0, 100:0, 150:0, 200:0}, "MIP-DEL": {10:5, 20:2, 30:2, 40:2, 50:2, 60:1, 70:2, 80:2, 90:1, 100:1, 150:0, 200:0}},
       "Final Optimal Gap": {"CP-RANK-ADD": {10:9.99990066621315E-05, 20:0.542071005612056, 30:0.534050542950223, 40:0.766514576978076, 50:0.853956337471085, 60:0.928684125083515, 70:0.98560468454184, 80:0.973344609799195, 90:0.935050472715018, 100:1, 150:1, 200:1}, "CP-ADD": {10:0, 20:0, 30:0.460324050491588, 40:0.69498065316858, 50:0.824921749351021, 60:0.984589642951132, 70:0.988794428624302, 80:0.989911458521626, 90:0.990184304754058, 100:0.991097081308148, 150:0.998056015035236, 200:0.999729414053561}, "DIDP-ADD": {10:0, 20:0, 30:0, 40:0.148328950637241, 50:0.191209256400639, 60:0.30605325107712, 70:0.401507280970434, 80:0.410132704395234, 90:0.425698505637481, 100:0.49541235183874, 150:0.565268179751511, 200:0.636165406689883}, "MIP-ADD": {10:0.5, 20:0, 30:0.703109847282323, 40:0.643525864534103, 50:0.890048933451511, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}, "CP-RANK-DEL": {10:7.90164318371821E-05, 20:0.53801319993339, 30:0.540024011996703, 40:0.561380546942935, 50:0.849249790677998, 60:0.938297182002129, 70:0.985913115889513, 80:1, 90:0.990288484626454, 100:1, 150:1, 200:1}, "CP-DEL": {10:0, 20:0.241353936718175, 30:0.93920858045596, 40:0.963369276449445, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}, "DIDP-DEL": {10:0, 20:0.234558045505559, 30:0.652992340964219, 40:0.863208290614357, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:0.926934108594099, 200:1}, "MIP-DEL": {10:-9.70242848074888E-07, 20:0.26995692287037, 30:0.837425154817263, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}},
       "Final Primal Gap":{"CP-RANK-ADD": {10:0.0030448224911316, 20:0.0225211823512353, 30:0.0451689574425507, 40:0.154743334619312, 50:0.225337616059574, 60:0.351642282512026, 70:0.400618888024236, 80:0.433873902569323, 90:0.468599563557826, 100:0.500726978540904, 150:0.612165272994472, 200:0.666220098948555}, "CP-ADD": {10:0, 20:0, 30:0.034991704943033, 40:0.033122402595101, 50:0.0640590073078607, 60:0.0972654006425769, 70:0.120991508527083, 80:0.152575409472662, 90:0.156551064261881, 100:0.150817191553019, 150:0.722517438291175, 200:0.556628821389561}, "DIDP-ADD": {10:0.00304502945390473, 20:0.00151346609794534, 30:0.000241710228659356, 40:0, 50:0, 60:0, 70:0.000172893378807992, 80:0.00576905464881116, 90:0, 100:0, 150:0.000358829413408322, 200:0}, "MIP-ADD": {10:0.50000066905643, 20:0.00106230285395708, 30:0.526779045268102, 40:0.340306375291392, 50:0.777705664584182, 60:1, 70:0.889812024672113, 80:1, 90:1, 100:1, 150:1, 200:1}, "CP-RANK-DEL": {10:0.0030448224911316, 20:0.00151338161677183, 30:0.0629799336369422, 40:0.187427602434623, 50:0.252271224079371, 60:0.311994130238711, 70:0.411408481409774, 80:0.43049763023241, 90:0.454258026090187, 100:0.505973542390159, 150:0.610923727260037, 200:0.655920083992779}, "CP-DEL": {10:0, 20:0.00662251655629139, 30:-0.0450177604047889, 40:0.429754297075133, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}, "DIDP-DEL": {10:0.00304502945390473, 20:0.00151346609794534, 30:0.385801793422016, 40:0.72560825519164, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:0.838522039759706, 200:1}, "MIP-DEL": {10:0.00304398110964756, 20:0.0802606519775395, 30:0.73083390341988, 40:1, 50:1, 60:1, 70:1, 80:1, 90:1, 100:1, 150:1, 200:1}}}

num_nodes = [10,20,30,40,50,60,70,80,90,100,150,200]

# for alg in res["Proven Optimal or Infeasible"]:
#   for i in num_nodes:
#     res["Proven Optimal or Infeasible"][alg][i] = 0
#     res_nof["Proven Optimal or Infeasible"][alg][i] = 0

# for i in data:
#     instance = data[i]["instance"].split(".json")[0]
#     if "random" in instance:
#       alg = data[i]["algorithm"]
#       if alg == "DIDP-ADD":
#           best_per_instance[instance] = data[i]["best_primal"]

# unique = set()

# for i in data:
#     instance = data[i]["instance"].split(".json")[0]
    
#     alg = data[i]["algorithm"]
#     # unique_id = instance+alg
#     if "random" in instance:
#       # unique.add(unique_id)
#       # n = data[i]["nodes"]
#       # if "MIP" in alg:
#       n = int(instance.split("-")[1])
#       best_of_instance = best_per_instance[instance]
#       primal = data[i]["best_primal"]
#       dual = data[i]["best_dual"]

#       if data[i]["time"] < 1798 and (data[i]["optimal"] == True or data[i]["infeasible"] == True): #proven opt/infeas
#         if n in res["Proven Optimal or Infeasible"][alg]:
#           res["Proven Optimal or Infeasible"][alg][n] += 1
#         else:
#           res["Proven Optimal or Infeasible"][alg][n] = 1      
#       if data[i]["infeasible"] == False:
#         opt_gap = (primal-dual)/max(1,primal)
#         primal_gap = (primal-best_of_instance)/max(1,primal)
        
#         if abs(primal_gap) < 0.1:
#            primal_gap = 0
#         elif primal_gap < 0:
#            primal_gap = 1

#         if opt_gap < 0:
#           opt_gap = 1

#         if n in res["Final Optimal Gap"][alg]:
#           res["Final Optimal Gap"][alg][n].append(opt_gap)
#         else:
#           res["Final Optimal Gap"][alg][n] = [opt_gap]
#         if n in res["Final Primal Gap"][alg]:
#           res["Final Primal Gap"][alg][n].append(primal_gap)
#         else:
#           res["Final Primal Gap"][alg][n] = [primal_gap]
#         if opt_gap < 0 or primal_gap < 0:

#           print(i)
#           print(primal)
#           print(dual)
#           print(best_of_instance)
#           print((primal-dual)/max(1,primal))
#           print((primal-best_of_instance)/max(1,primal))

# print(sorted(list(unique)))

# for i in data_nof:
#     instance = data_nof[i]["instance"].split(".json")[0]
#     if "random" in instance:
#       alg = data_nof[i]["algorithm"]
#       # n = data_nof[i]["nodes"]
#       # if "MIP" in alg:
#       n = int(instance.split("-")[1])
#       best_of_instance = best_per_instance[instance]
#       primal = data_nof[i]["best_primal"]
#       dual = data_nof[i]["best_dual"]

#       if data_nof[i]["time"] < 1798 and (data_nof[i]["optimal"] == True or data_nof[i]["infeasible"] == True): #proven opt/infeas
#         if n in res_nof["Proven Optimal or Infeasible"][alg]:
#           res_nof["Proven Optimal or Infeasible"][alg][n] += 1
#         else:
#           res_nof["Proven Optimal or Infeasible"][alg][n] = 1      
#       if data_nof[i]["infeasible"] == False:
#         opt_gap = (primal-dual)/max(1,primal)
#         primal_gap = (primal-best_of_instance)/max(1,primal)
        
#         if abs(primal_gap) < 0.1:
#            primal_gap = 0
#         elif primal_gap < 0:
#            primal_gap = 1

#         if abs(primal_gap) > 0.1 and primal == 0:
#           opt_gap = 1
#         elif opt_gap < 0:
#           opt_gap = 1

#         if n in res_nof["Final Optimal Gap"][alg]:
#           res_nof["Final Optimal Gap"][alg][n].append(opt_gap)
#         else:
#           res_nof["Final Optimal Gap"][alg][n] = [opt_gap]
#         if n in res_nof["Final Primal Gap"][alg]:
#           res_nof["Final Primal Gap"][alg][n].append(primal_gap)
#         else:
#           res_nof["Final Primal Gap"][alg][n] = [primal_gap]
#         if opt_gap < 0.2 or primal_gap < 0:
#           print(alg)
#           print(i)
#           print(primal)
#           print(dual)
#           print(best_of_instance)
#           print((primal-dual)/max(1,primal))
#           print((primal-best_of_instance)/max(1,primal))

# for alg in res["Final Optimal Gap"]:
#    for n in res["Final Optimal Gap"][alg]:
#       # print(alg, n)
#       if "MIP" in alg and n > 100:
#         res["Final Optimal Gap"][alg][n] = 1
#         res["Final Primal Gap"][alg][n] = 1
#         res_nof["Final Optimal Gap"][alg][n] = 1
#         res_nof["Final Primal Gap"][alg][n] = 1
#       else:
#         res["Final Optimal Gap"][alg][n] = sum(res["Final Optimal Gap"][alg][n])/len(res["Final Optimal Gap"][alg][n])
#         res["Final Primal Gap"][alg][n] = sum(res["Final Primal Gap"][alg][n])/len(res["Final Primal Gap"][alg][n])
#         res_nof["Final Optimal Gap"][alg][n] = sum(res_nof["Final Optimal Gap"][alg][n])/len(res_nof["Final Optimal Gap"][alg][n])
#         res_nof["Final Primal Gap"][alg][n] = sum(res_nof["Final Primal Gap"][alg][n])/len(res_nof["Final Primal Gap"][alg][n])

# print(res)



graphboth_df = pd.DataFrame.from_dict(res)
graphboth_nof_df = pd.DataFrame.from_dict(res_nof)

# print(graphboth_df)
# print(graphboth_nof_df)

# font_path = r"C:\Users\Daniel\Downloads\lm\lm\fonts\opentype\public\lm\lmroman12-bold.otf"  # Your font path goes here
# font_manager.fontManager.addfont(font_path)
# prop = font_manager.FontProperties(fname=font_path)

sns.set_theme(style="ticks")

# Define the palette as a list to specify exact values
palette = sns.color_palette("husl", 9)

cols1 = ["DIDP Add", "CP Rank Add", "CP Rank Del", "MIP Del", "MIP Add", "CP Interval Del", "CP Interval Add","DIDP Del"]
cols = ["DIDP Add", "CP Rank Add", "CP Rank Del", "MIP Add", "MIP Del", "CP Interval Add", "CP Interval Del", "DIDP Del"]

translate = {"DIDP Add":"DIDP-ADD",
       "DIDP Del":"DIDP-DEL",
       "CP Interval Add":"CP-ADD",
       "CP Interval Del":"CP-DEL",
       "CP Rank Add":"CP-RANK-ADD",
       "CP Rank Del":"CP-RANK-DEL",
       "MIP Add":"MIP-ADD",
       "MIP Del":"MIP-DEL"}

clrs = sns.color_palette("hls", 8)
colours = {}

for i,clr in enumerate(clrs):
   colours[cols1[i]] = clr

##Proven Optimal or Infeasible VS N (BY FIRST/LAST)


# Plot the lines on two facets
fig, axs = plt.subplots(figsize=(13, 5),ncols=2)
# ax.yaxis.set_major_formatter(ticker.EngFormatter())
for alg in translate:
    # print(list(res["Proven Optimal or Infeasible"][translate[alg]].keys()))
    # print(list(res["Proven Optimal or Infeasible"][translate[alg]].values()))
    sns.lineplot(x = res["Proven Optimal or Infeasible"][translate[alg]].keys(), y = res["Proven Optimal or Infeasible"][translate[alg]].values(), label = str(alg), color=colours[alg], linewidth=2.5,zorder = 9-i,ax=axs[0], path_effects=[pe.Stroke(linewidth=3, foreground='white',alpha=1), pe.Normal()])
    sns.lineplot(x = res_nof["Proven Optimal or Infeasible"][translate[alg]].keys(), y = res_nof["Proven Optimal or Infeasible"][translate[alg]].values(), label = str(alg), color=colours[alg], linewidth=2.5,zorder = 9-i,ax=axs[1], path_effects=[pe.Stroke(linewidth=3, foreground='white',alpha=1), pe.Normal()])
    print(alg)
    print(sum(res["Proven Optimal or Infeasible"][translate[alg]].values()))
    print(sum(res_nof["Proven Optimal or Infeasible"][translate[alg]].values()))

sns.despine()

# fig.suptitle('Proven Infeasible or Optimal Over Time', fontsize=18) # or plt.suptitle('Main title')
axs[0].set_xlim(0,200)
axs[0].set_ylim(-1,6)
# axs[1].ylim(0,60)
axs[0].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

axs[0].axes.grid(visible=True)
axs[0].axes.set_title("With First/Last Vertex Restrictions", fontsize=16)
axs[0].axes.tick_params(axis='both', labelsize=14)
axs[0].axes.set(xlabel='Number of Vertices', ylabel='Proven Optimal or Infeasible')
axs[0].axes.xaxis.label.set_size(16)
axs[0].axes.yaxis.set_major_locator(ticker.MultipleLocator(5))
axs[0].axes.xaxis.set_major_locator(ticker.MultipleLocator(50))
axs[1].axes.xaxis.set_major_locator(ticker.MultipleLocator(50))
axs[0].axes.yaxis.label.set(fontsize='16')
axs[0].get_legend().set_visible(False)
# sns.move_legend(axs[0], "upper left", bbox_to_anchor=(1, 1))
# plt.setp(axs[0].get_legend().get_texts(), fontsize='14') # 

axs[1].set_xlim(0,200)
axs[1].set_ylim(-1,6)
# axs[1].ylim(0,60)
axs[1].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

axs[1].set_title("Without First/Last Vertex Restrictions", fontsize=16)
axs[1].tick_params(axis='both', labelsize=14)
axs[1].set(xlabel='Number of Vertices', ylabel='')
axs[1].xaxis.label.set_size(16)
axs[1].yaxis.set_major_locator(ticker.MultipleLocator(5))
axs[1].yaxis.label.set(fontsize='16')
sns.move_legend(axs[1], "upper left", bbox_to_anchor=(1, 1))
plt.setp(axs[1].get_legend().get_texts(), fontsize='14') # 

plt.show()


# #FINAL OPT GAP VS N (BY FIRST/LAST)
# # Plot the lines on two facets
# fig, axs = plt.subplots(figsize=(13, 5),ncols=2)
# # ax.yaxis.set_major_formatter(ticker.EngFormatter())
# for alg in translate:
#     # print(list(res["Proven Optimal or Infeasible"][translate[alg]].keys()))
#     # print(list(res["Proven Optimal or Infeasible"][translate[alg]].values()))
#     sns.lineplot(x = res["Final Optimal Gap"][translate[alg]].keys(), y = res["Final Optimal Gap"][translate[alg]].values(), label = str(alg), color=colours[alg], linewidth=2.5,zorder = 9-i,ax=axs[0], path_effects=[pe.Stroke(linewidth=3, foreground='white',alpha=1), pe.Normal()])
#     sns.lineplot(x = res_nof["Final Optimal Gap"][translate[alg]].keys(), y = res_nof["Final Optimal Gap"][translate[alg]].values(), label = str(alg), color=colours[alg], linewidth=2.5,zorder = 9-i,ax=axs[1], path_effects=[pe.Stroke(linewidth=3, foreground='white',alpha=1), pe.Normal()])
#     # print(alg)
#     # print(sum(res["Final Optimal Gap"][translate[alg]].values()))
#     # print(sum(res_nof["Final Optimal Gap"][translate[alg]].values()))

# sns.despine()

# # fig.suptitle('Proven Infeasible or Optimal Over Time', fontsize=18) # or plt.suptitle('Main title')
# axs[0].set_xlim(0,200)
# axs[0].set_ylim(-0.1,1.1)
# # axs[1].ylim(0,60)
# axs[0].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

# axs[0].axes.grid(visible=True)
# axs[0].axes.set_title("With First/Last Vertex Restrictions", fontsize=16)
# axs[0].axes.tick_params(axis='both', labelsize=14)
# axs[0].axes.set(xlabel='Number of Vertices', ylabel='Optimality Gap')
# axs[0].axes.xaxis.label.set_size(16)
# axs[0].axes.yaxis.set_major_locator(ticker.MultipleLocator(0.25))
# axs[0].axes.yaxis.label.set(fontsize='16')
# axs[0].get_legend().set_visible(False)
# # sns.move_legend(axs[0], "upper left", bbox_to_anchor=(1, 1))
# # plt.setp(axs[0].get_legend().get_texts(), fontsize='14') # 
# # plt.xticks(num_nodes)
# # axs[1].xticks(num_nodes)
# axs[1].set_xlim(0,200)
# axs[1].set_ylim(-0.1,1.1)
# # axs[1].ylim(0,60)
# axs[1].grid(True, which='major', axis='both', linestyle='--', linewidth=0.7) 

# axs[1].set_title("Without First/Last Vertex Restrictions", fontsize=16)
# axs[1].tick_params(axis='both', labelsize=14)
# axs[1].set(xlabel='Number of Vertices', ylabel='')
# axs[1].xaxis.label.set_size(16)
# axs[1].yaxis.set_major_locator(ticker.MultipleLocator(0.25))
# axs[1].yaxis.label.set(fontsize='16')
# sns.move_legend(axs[1], "upper left", bbox_to_anchor=(1, 1))
# plt.setp(axs[1].get_legend().get_texts(), fontsize='14') # 

# plt.show()

#FINAL PRIMAL GAP VS N (BY FIRST/LAST)

