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

def tsp_plot(sequence, locations, c):

  x = [i[0] for i in locations.values()]
  y = [i[1] for i in locations.values()]

  fig, ax = plt.subplots()      # Prepare 2 plots
  ax.set_title('Optimized tour')
  ax.scatter(x, y)             # plot B
  prev_node = sequence[-1]
  # distance = 
  for i in sequence:
      start_pos = locations[prev_node]
      end_pos = locations[i]
      ax.annotate("",
              xy=start_pos, xycoords='data',
              xytext=end_pos, textcoords='data',
              arrowprops=dict(arrowstyle="->",
                              connectionstyle="arc3", color='red'))
      #distance += np.linalg.norm(end_pos - start_pos)
      prev_node = i

  textstr = "N nodes: %d\nTotal length: %.0f" % (len(sequence), c)
  props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
  ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=8, # Textbox
          verticalalignment='top', bbox=props)

  plt.tight_layout()
  plt.show()