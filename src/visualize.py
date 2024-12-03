import docplex.cp.utils_visu as visu

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