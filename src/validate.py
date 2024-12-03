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

def checkRemovedEdges(sequence_list, delete_dict):
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