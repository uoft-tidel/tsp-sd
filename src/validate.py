def checkFirst(interval):
  #start and end of first in is 0
  #(start, end, size)
  return interval[0] == 0 and interval[1] == 0 

def checkSequence(sequence_list):
  #Check each value is used (1 to n-1)
  #Check sequence makes sense
  #Also checks last value is dummy node at end

  #sequence_list as dict: {i:j, j:k, k:l ... }

  i = 0
  j = 0
  used_numbers = set()
  while i != len(sequence_list):
    i = sequence_list[i]
    used_numbers.add(i)
    j += 1

  #checks n+1 is last number and each number used once
  return j == len(sequence_list) and len(used_numbers) == len(sequence_list)

def checkLength(traverse_list,last_in):
  length = last_in[1]
  l = 0
  for i in traverse_list:
    l += traverse_list[i][2]
  return length == l

def checkLengthDIDP(sequence, c):
  sequence = [int(x) for x in sequence]
  prev_node = sequence[0]
  l = c[prev_node][sequence[-1]]
  for cur_node in sequence[1:]:
    l += c[prev_node][cur_node]
    prev_node = cur_node
  return l

def checkRemovedEdgesDIDP(sequence_list, delete_dict):
  removed_edges = set()
  prev_node = sequence_list[0]
  for j in delete_dict[prev_node]:
    removed_edges.add((j[0],j[1]))

  for i in range(1,len(sequence_list)):
    cur_node = sequence_list[i]

    #check if current->next isn't deleted
    if (prev_node, cur_node) not in removed_edges and (cur_node, prev_node) not in removed_edges:
      #go to next
      #add deleted edges to removed_edges
      for j in delete_dict[cur_node]:
        removed_edges.add((j[0],j[1]))
      prev_node = cur_node

    else:
      print("ARC: ", prev_node," -> ",cur_node)
      return False
    
  #completing the cycle
  cur_node = sequence_list[0]
  if (prev_node, cur_node) not in removed_edges and (cur_node, prev_node) not in removed_edges:
    return True
  else:
    return False

  # i = 0
  # #go until next value is dummy end node (never deleted)
  # while sequence_list[i] < len(sequence_list):
  #   
  #   else:
  #     return False
  
  # return True

def checkRemovedEdgesCP(sequence_list, delete_dict):
  removed_edges = set()
  i = 0
  #go until next value is dummy end node (never deleted)
  while sequence_list[i] < len(sequence_list):
    #check if current->next isn't deleted
    if (i, sequence_list[i]) not in removed_edges:
      #go to next
      i = sequence_list[i]
      #add deleted edges to removed_edges
      for j in delete_dict[str(i)]:
        removed_edges.add((int(j[0]),int(j[1])))
    else:
      return False
  
  return True