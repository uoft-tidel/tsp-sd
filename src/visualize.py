import docplex.cp.utils_visu as visu
import matplotlib.pyplot as plt
import numpy as np


def tsp_as_jobshop(res,traverse,n):
  #if res and visu.is_visu_enabled():
  # Draw solution
  visu.timeline('TSP-SD')
  visu.panel('Traverses')
  for m in range(n+1):
      visu.sequence(name='From ' + str(m))
      for a in traverse:
          if a[0]==m:
              itv = res.get_var_solution(traverse[a])
              if itv.is_present():
                  if a[0] == 0:
                    start = "start"
                  else:
                    start = a[0]
                  if a[1] == n+1:
                    end = "end"
                  else:
                    end = a[1]
                  visu.interval(itv, a[0], '{}=>{}'.format(start,end))
  visu.show()

def tsp_plot(instance_name, sequence, locations, c):

  x = [i[0] for i in locations.values()]
  y = [i[1] for i in locations.values()]

  fig, ax = plt.subplots()   
  plt.style.use('bmh')
  ax.set_title('Optimized tour')
  ax.scatter(x, y)             # plot B
  prev_node = sequence[-1]
  # distance = 
  for ind, i  in enumerate(sequence[1:]):
      start_pos = locations[prev_node]
      end_pos = locations[i]
      if ind == len(sequence)-2:
        ax.annotate("",
                xy=start_pos, xycoords='data',
                xytext=end_pos, textcoords='data',
                arrowprops=dict(arrowstyle="->", color="red",
                                connectionstyle="arc3"))
      else:
         ax.annotate("",
                xy=start_pos, xycoords='data',
                xytext=end_pos, textcoords='data',
                arrowprops=dict(arrowstyle="-|>", color="slategray",
                                connectionstyle="arc3"))
      #distance += np.linalg.norm(end_pos - start_pos)
      prev_node = i

  textstr = "Instance: %s N nodes: %d\nTotal length: %.0f" % (instance_name.split(".json")[0], len(sequence)-1, c)
  props = dict(boxstyle='round', alpha=0.3)
  ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=8, # Textbox
          verticalalignment='top', bbox=props)

  plt.tight_layout()
  plt.show()