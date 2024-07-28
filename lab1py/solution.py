import sys
from collections import deque
from decimal import Decimal
from queue import PriorityQueue
 

#Parse input for transitions
#For guidance used https://www.vipinajayakumar.com/parsing-text-with-python/
def parse_input(input):
   next_states_list = deque()
   if ": " in input:
      state, next_states = input.split(": ")
      for state_cost in next_states.split():
         next_state, cost = state_cost.split(",")
         next_states_list.append((next_state, int(cost)))
   else:
      state = input.rstrip(':')
   return state, next_states_list

#For guidance used https://www.w3schools.com/python/ref_func_sorted.asp
def expand_state(curr_node, transitions):
   if curr_node[0]  in transitions:
      return sorted(transitions[curr_node[0]], key=lambda x: x[0]) #return alphabeticaly sorted list 
   return None

def expand_state_ucs_a(curr_node, curr_cost, transitions):
   if curr_node  in transitions:
      children = []
      transition = transitions[curr_node]
      for next_state, next_cost in transition:
            children.append((next_state, next_cost)) #update of total_cost is done in calling function: have only part of expand function(ality) here
      return children  
   return None

##For guidance used https://www.baeldung.com/cs/dfs-vs-bfs-vs-dijkstra
#TRACK PATH AND TOTAL COST FOR BFS
def track_path_bfs(child_parent_dictionary, initial_state, final_state):
   path = deque()
   total_cost = Decimal(0)
   
   curr_state = final_state #from final state
   while curr_state != initial_state[0]: #go to initial state
      path.append(curr_state) #track path
      #get parent
      parent_cost = child_parent_dictionary[curr_state]
      #update current node and total cost
      curr_state = parent_cost[0]
      total_cost += parent_cost[1]
      
               
   path.append(initial_state[0])
   path.reverse()
      
   return path, total_cost
  
#TRACK PATH FOR UCS
#I keep track of total cost in calling function, here I only track path with the same logic as for bfs
def track_path_ucs_a(child_parent_dictionary, initial_state, final_state):
   path = deque()
   
   curr_node = final_state
   curr_state = curr_node[0]
   curr_cost = curr_node[1]
   while curr_state != initial_state[0]:
      path.append(curr_state)
      parent_node = child_parent_dictionary[curr_node]
      curr_state = parent_node[0]
      curr_cost = parent_node[1]
      curr_node = parent_node
                 
   path.append(initial_state[0])
   path.reverse()
      
   return path  

#BFS
def breadth_first_search(file_name):
   
   #read lines from file
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define variables for parsing
   initial_state = None #only one variable
   final_states = deque() #queue with only state as value
   transitions = dict() # (state, queue:(next, cost))
   count = 0
   
   for line in lines:
      stripped_line = line.strip()
      if "#" in stripped_line:
         continue
      else:
         if count == 0:
            initial_state = (stripped_line, 0)
         elif count == 1:
            final_states_input = stripped_line.split(" ")
            for final_state in final_states_input:
               final_states.append(final_state)
         else:
            state, next_states_list = parse_input(stripped_line)
            transitions[state] = next_states_list
      count += 1
   
   #define variables for algorithm
   found_solution = False
   child_parent_dictionary = dict() #child_node: (parent_node, cost)       
   open_nodes = deque() #(state, cost)
   open_nodes_dict = dict() #node: cost - for faster search if child node is already in open_nodes
   closed = dict() #state:cost
   
   #algorithm ---------------------------------------------------------------------------------------------------------
   open_nodes.append((initial_state[0], initial_state[1]))
   open_nodes_dict[initial_state[0]] = initial_state[1]
   
   while open_nodes != []:
      curr_node = open_nodes.popleft()
      open_nodes_dict.pop(curr_node[0])
      
      if curr_node[0] in final_states:
         found_solution = True
         closed[curr_node[0]] = curr_node[1]
         final_final_state = curr_node[0]
         break
      
      closed[curr_node[0]] = curr_node[1]
      
      for child_node in expand_state(curr_node, transitions):
         #print("Child node: ", child_node[0], "Cost: ", child_node[1])
         if child_node[0] not in closed: #if not already visited
            if child_node[0] not in open_nodes_dict: #if not already in open (don't want duplicates in open_nodes)
               open_nodes.append((child_node[0], child_node[1]))
               open_nodes_dict[child_node[0]] = child_node[1]
               child_parent_dictionary[child_node[0]] = (curr_node[0], child_node[1])
            
   
   if found_solution:   
      
      #Find shortest path
      path, total_cost = track_path_bfs(child_parent_dictionary, initial_state, final_final_state)
        
      print("# BFS")
      print("[FOUND_SOLUTION]: yes")
      print("[STATES_VISITED]: ", len(closed))
      print("[PATH_LENGTH]: ", len(path))
      print("[TOTAL_COST]: ", round(total_cost, 1))
      print("[PATH]: ", end = '')
      count = 0
      for state in path:
         if count == 0:
            print(state, end='')
         else:
            print(" => ", state, end = '')
         count = count + 1
   else:
      print("[FOUND_SOLUTION]: no")
   
   #-------------------------------------------------------------------------------------------------------------------      
         
         
#UCS
def uniform_cost_search(file_name):
   
   #read lines from file
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define variables for parsing
   initial_state = None # (state, 0)
   final_states = deque() #queue with only state as value
   transitions = dict() # (state, queue:(next, cost))
   count = 0
   
   for line in lines:
      stripped_line = line.strip()
      if "#" in stripped_line:
         continue
      else:
         if count == 0:
            initial_state = (stripped_line, 0)
         elif count == 1:
            final_states_input = stripped_line.split(" ")
            for final_state in final_states_input:
               final_states.append(final_state)
         else:
            state, next_states_list = parse_input(stripped_line)
            transitions[state] = next_states_list
      count += 1
   
   
   #define variables for algorithm
   found_solution = False
   child_parent_dictionary = dict() #(child_state, total_cost): (parent_state, parent_cost)      
   open_nodes =  PriorityQueue() #(total_cost, state) - for faster search if child node is already in open_nodes
   closed = set() #state
   total_cost = Decimal(0)
   
   #algorithm ---------------------------------------------------------------------------------------------------------
   
   open_nodes.put((initial_state[1], initial_state[0]))
   
   while open_nodes:
      
      current = open_nodes.get()
      curr_node = current[1]
      curr_cost = current[0]
      
      if curr_node in final_states:
         found_solution = True
         closed.add(curr_node)
         total_cost += curr_cost
         final_final_state = (curr_node, total_cost)
         break
      
      closed.add(curr_node)
      
      for child_node in expand_state_ucs_a(curr_node, curr_cost, transitions):
         
         child_state, child_cost = child_node
         if child_state not in closed:
            tc = child_cost + curr_cost
            open_nodes.put((tc, child_state))  
            child_parent_dictionary[child_state, tc] = (curr_node, curr_cost)

   if found_solution:   
      
      #Find shortest path
      path = track_path_ucs_a(child_parent_dictionary, initial_state, final_final_state)
        
      print("# UCS")
      print("[FOUND_SOLUTION]: yes")
      print("[STATES_VISITED]: ", len(closed))
      print("[PATH_LENGTH]: ", len(path))
      print("[TOTAL_COST]: ", round(total_cost, 1))
      print("[PATH]: ", end = '')
      count = 0
      for state in path:
         if count == 0:
            print(state, end='')
         else:
            print(" => ", state, end = '')
         count = count + 1
   else:
      print("[FOUND_SOLUTION]: no")

#ASTAR
def astar(file_name, file_name_heuristic):
   
   #read lines from file_name
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define variables for parsing
   initial_state = None # (state, 0)
   final_states = deque() #queue with only state as value
   transitions = dict() # (state, queue:(next, cost))
   count = 0
   heuristic_dict = dict()
   
   for line in lines:
      stripped_line = line.strip()
      if "#" in stripped_line:
         continue
      else:
         if count == 0:
            initial_state = (stripped_line, 0)
         elif count == 1:
            final_states_input = stripped_line.split(" ")
            for final_state in final_states_input:
               final_states.append(final_state)
         else:
            state, next_states_list = parse_input(stripped_line)
            transitions[state] = next_states_list
      count += 1
   
   #read lines from file_name_heuristic
   file = open(file_name_heuristic, "r", encoding = "utf-8")
   lines = file.readlines()
   
   for line in lines:
      state, heuristic_value = line.split(":")
      heuristic_dict[state.strip()] = Decimal(heuristic_value.strip())
      
   #define variables for algorithm
   found_solution = False
   child_parent_dictionary = dict() #(child_state, total_cost): (parent_state, parent_cost)      
   open_nodes =  PriorityQueue() #(total_cost + h, total_cost, state) - for faster search 
   open_nodes_dict = dict() #state: total_cost - for faster search only if child node is already in open_nodes
   open_nodes_set = set() #state - for faster search only if child node is already in open_nodes
   closed = dict() #state
   total_cost = Decimal(0)
   
   #algorithm ---------------------------------------------------------------------------------------------------------
   
   open_nodes.put((Decimal(0), Decimal(initial_state[1]), initial_state[0]))
   open_nodes_dict[initial_state[0]] = Decimal(initial_state[1])
   open_nodes_set.add(initial_state[0])
   
   while open_nodes:
      
      current = open_nodes.get()
      
      curr_node = current[2]
      curr_cost = current[1]
      curr_cost_heuristic = current[0] #not relevant
      open_nodes_dict.pop(curr_node)
      open_nodes_set.remove(curr_node)
      
      if curr_node in final_states:
         found_solution = True
         closed[curr_node] = curr_cost
         total_cost += curr_cost
         final_final_state = (curr_node, total_cost)
         break
      
      closed[curr_node] = curr_cost
      
      for child_node in expand_state_ucs_a(curr_node, curr_cost, transitions):
         
         child_state, child_cost = child_node
         heuristic_value = heuristic_dict.get(child_state) #or parent?
         tc = child_cost + curr_cost
         tc_heuristic = child_cost + curr_cost + heuristic_value
            
         if child_state in closed or child_state in open_nodes_set:
            
            if(child_state in closed):
               prev_tc = closed.get(child_state)
            else: 
               prev_tc = open_nodes_dict.get(child_state)
            
            if prev_tc < tc:
               continue
            else:
               #found cheaper way, remove the one we found before
               open_nodes_set.remove(child_state) 
               open_nodes_dict.pop(child_state)
                     
            
         #insert new/updated node in open list
         open_nodes.put((tc_heuristic, tc, child_state))
         open_nodes_dict[child_state] = tc
         open_nodes_set.add(child_state)
         child_parent_dictionary[child_state, tc] = (curr_node, curr_cost)

   if found_solution:   
      
      #Find shortest path
      path = track_path_ucs_a(child_parent_dictionary, initial_state, final_final_state)
        
      print("# A-STAR ", file_name_heuristic)
      print("[FOUND_SOLUTION]: yes")
      print("[STATES_VISITED]: ", len(closed))
      print("[PATH_LENGTH]: ", len(path))
      print("[TOTAL_COST]: ", round(total_cost, 1))
      print("[PATH]: ", end = '')
      count = 0
      for state in path:
         if count == 0:
            print(state, end='')
         else:
            print(" => ", state, end = '')
         count = count + 1
   else:
      print("[FOUND_SOLUTION]: no")
      
#CHECK OPTIMISTIC 
def check_optimistic(file_name, file_name_heuristic): 
   
   #read lines from file_name_heuristic
   file = open(file_name_heuristic, "r", encoding = "utf-8")
   lines = file.readlines()
   
   heuristic_dict = dict()
   for line in lines:
      state, heuristic_value = line.split(":")
      heuristic_dict[state.strip()] = Decimal(heuristic_value.strip()) 
   
   #read lines from file_name
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define variables for parsing
   final_states = deque() #queue with only state as value
   transitions = dict() # (state, queue:(next, cost))
   count = 0
   
   for line in lines: 
      #print("Line: ", line)
      stripped_line = line.strip()
      if "#" in stripped_line:
         continue
      else:
         if count == 0:
            #initial state
            count += 1
            continue
         elif count == 1:
            final_states_input = stripped_line.split(" ")
            for final_state in final_states_input:
               final_states.append(final_state)
         else:
            state, next_states_list = parse_input(stripped_line)
            transitions[state] = next_states_list
      count += 1

   print("# HEURISTIC-OPTIMISTIC ", file_name_heuristic)
   #do ucs for every node in file_name_heuristic

   found_error = False
   for node, heuristic_value in heuristic_dict.items():
      
      initial_state = (node, 0)
      
      #define variables for algorithm
      child_parent_dictionary = dict() #(child_state, total_cost): (parent_state, parent_cost)      
      open_nodes =  PriorityQueue() #(total_cost, state) - for faster search if child node is already in open_nodes
      closed = set() #state
      total_cost = Decimal(0)
   
      #UCS algorithm ---------------------------------------------------------------------------------------------------------
      open_nodes.put((initial_state[1], initial_state[0]))
   
      while open_nodes:
         
         current = open_nodes.get()
         curr_node = current[1]
         curr_cost = current[0]
      
         if curr_node in final_states:
            closed.add(curr_node)
            total_cost += curr_cost
            break
      
         closed.add(curr_node)
      
         for child_node in expand_state_ucs_a(curr_node, curr_cost, transitions):
         
            child_state, child_cost = child_node
            if child_state not in closed:
               tc = child_cost + curr_cost
               open_nodes.put((tc, child_state))  
               child_parent_dictionary[child_state, tc] = (curr_node, curr_cost)

      #check condition
      err = False
      heuristic_value = heuristic_dict.get(initial_state[0])
      if total_cost < heuristic_value:
        err = True
        found_error = True
   
      #print output
      print("[CONDITION]: ", end='')
      if err: print("[ERR] ", end='') 
      else: print("[OK] ",end='')  
      print(f"h({initial_state[0]}) <= h*: {heuristic_value:.1f} <= {total_cost:.1f}")
   
   #print conclusion
   if found_error: print("[CONCLUSION]: Heuristic is not optimistic.")
   else: print("[CONCLUSION]: Heuristic is optimistic.")

#CHECK CONSISTENT
def check_consistent(file_name, file_name_heuristic):
   
   #read lines from file_name_heuristic
   file = open(file_name_heuristic, "r", encoding = "utf-8")
   lines = file.readlines()
   
   heuristic_dict = dict()
   for line in lines:
      state, heuristic_value = line.split(":")
      heuristic_dict[state.strip()] = Decimal(heuristic_value.strip()) 
   
   #read lines from file_name
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define variables for parsing
   transitions = dict() # (state, queue:(next, cost))
   count = 0
   
   for line in lines: 
      #print("Line: ", line)
      stripped_line = line.strip()
      if "#" in stripped_line:
         continue
      else:
         if count == 0:
            #initial state
            count += 1
            continue
         elif count == 1:
            #final states
            count += 1
            continue
         else:
            state, next_states_list = parse_input(stripped_line)
            transitions[state] = next_states_list
      count += 1

   print("# HEURISTIC-CONSISTENT ", file_name_heuristic)
   found_err = False
   for state, next_states_list in transitions.items():
      
      state_heurisic = heuristic_dict.get(state)
      for next_state, next_cost in next_states_list:
         err = True
         next_state_heuristic = heuristic_dict.get(next_state)
         if (state_heurisic <= (next_state_heuristic +  next_cost)):
            err = False
         else:
            found_err = True
         
         #print output for condition
         print("[CONDITION]: ", end='')
         if err: print("[ERR] ", end='') 
         else: print("[OK] ",end='')  
         print(f"h({state}) <= h({next_state}) + c: {state_heurisic:.1f} <= {next_state_heuristic:.1f} + {next_cost:.1f}")
   
   #print conclusion
   if found_err: print("[CONCLUSION]: Heuristic is not consistent.")
   else: print("[CONCLUSION]: Heuristic is consistent.")
            
            


#For guidance used https://www.geeksforgeeks.org/python-main-function/
#For guidance used https://www.geeksforgeeks.org/take-input-from-stdin-in-python/
#For guidance used https://www.geeksforgeeks.org/command-line-arguments-in-python/
if __name__ == "__main__":
   
   #get arguments
   args = sys.argv
   
   #extract the .txt file name
   if '--ss' in args:
      index = args.index('--ss')
      file_name = args[index + 1]
   
   if '--h' in args:
      index = args.index('--h')
      file_name_heuristic = args[index + 1]
   
   
   #extract the algorithm name
   if '--alg' in args:
      index = args.index('--alg')
      algorithm_name = args[index + 1]
      if(algorithm_name == 'bfs'):
         breadth_first_search(file_name)
      elif(algorithm_name == 'ucs'): 
         uniform_cost_search(file_name)
      elif (algorithm_name == 'astar'):
         astar(file_name, file_name_heuristic)
   
   #optimistic check      
   if ('--check-optimistic' in args):
         check_optimistic(file_name, file_name_heuristic)
         
   #consistent check
   if('--check-consistent' in args):
      check_consistent(file_name, file_name_heuristic)
         