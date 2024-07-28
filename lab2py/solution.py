import sys
from collections import deque


#FOR GUIDANCE USED: https://www.w3schools.com/python/ref_set_intersection.asp
def selectClauses(clauses_start, sos_strategy, resolved):
   #clauses_start -> lista setova (lista klauzula)
   #sos_strategy -> lista setova (lista klauzula)
   #resolved -> dictionary (cl1, cl2): T
   selectedClause1 = set()
   selectedClause2 = set()
   for cl1 in sos_strategy:
      
      selectedClause1 = cl1.copy()
      
      found_cl2 = False
      for cl2 in clauses_start:
         #check if already resolved this pair
         key1 = (frozenset(cl1), frozenset(cl2))
         key2 = (frozenset(cl2), frozenset(cl1))
         if key1 in resolved or key2 in resolved:
            continue
         
         #negate all the literals in cl1
         cl1_negated = set()
         for lit in cl1:
            lit = lit.replace("~", "") if "~" in lit else "~" + lit
            cl1_negated.add(lit)
         
         #check if there are common elements in set1 and set2
         common_literals = cl1_negated.intersection(cl2)
         if len(common_literals) != 0:
            selectedClause2 = cl2.copy()
            found_cl2 = True
            break
      
      #if cl2 is in clauses_start, search is over -> break
      if found_cl2:
         break
      
      #if not, search for other clause in sos
      for cl2 in sos_strategy:
         if cl1 == cl2:
            continue
         
         #check if already resolved this pair
         key1 = (frozenset(cl1), frozenset(cl2))
         key2 = (frozenset(cl2), frozenset(cl1))
         if key1 in resolved or key2 in resolved:
            continue
         
         #negate all the literals in cl1
         cl1_negated = set()
         for lit in cl1:
            lit = lit.replace("~", "") if "~" in lit else "~" + lit
            cl1_negated.add(lit)
            
         #check if there are common elements in set1 and set2
         common_literals = cl1_negated.intersection(cl2)
         if len(common_literals) != 0:
            selectedClause2 = cl2.copy()
            #print("selectedClause2: ", selectedClause2)
            found_cl2 = True
            break
         
      if found_cl2 == False:
         continue
   
   #mark clauses as resolved
   resolved[(frozenset(selectedClause1), frozenset(selectedClause2))] = True
   resolved[(frozenset(selectedClause2), frozenset(selectedClause1))] = True
   
   #return clauses
   return selectedClause1, selectedClause2  
         
    
def plResolve(k1, k2):
   kl_combined = k1.union(k2)

   resolved_list = []
   for lit in k1:
      lit_neg = lit.replace("~", "") if "~" in lit else "~" + lit
      
      if lit_neg in kl_combined:
         kl_combined.remove(lit)
         kl_combined.remove(lit_neg)
         
         if len(kl_combined) == 0:
            resolved_list.append({"NIL"})
         else:
            resolved_list.append(kl_combined)
         
         kl_combined = k1.union(k2)

   return resolved_list
   
#FOR GUIDANCE USED: https://www.w3schools.com/python/ref_func_frozenset.asp 
#FOR GUIDANCE UDES: https://www.w3schools.com/python/ref_set_issubset.asp
def strategy_of_simplification(clauses_start, sos_strategy):
   
   #check for duplicates in combined_clauses
   clauses_start_copy = clauses_start.copy()
   sos_strategy_copy = sos_strategy.copy()
   for cl_start in clauses_start_copy:
      for cl_sos in sos_strategy_copy:
         if cl_start == cl_sos:
            clauses_start.remove(cl_start)
   
   combined_clauses = clauses_start+sos_strategy
   
   #check redundancy
   for lit_set1 in combined_clauses:
      for lit_set2 in combined_clauses:
         if lit_set1 != lit_set2 and lit_set1.issubset(lit_set2):
            combined_clauses.remove(lit_set2)
            if lit_set2 in clauses_start:
               clauses_start.remove(lit_set2)
            else:
               sos_strategy.remove(lit_set2)
             
   combined_clauses = combined_clauses
   
   #check tautology
   for lit_set in combined_clauses:
      found_tautology = False
      for el in lit_set:
         #take el, negate it, if exists, tautology found -> break
         el = el.replace("~", "") if "~" in el else "~" + el
         if el in lit_set:
            found_tautology=True
            break
      
      if found_tautology:
         combined_clauses.remove(lit_set)
         if lit_set in clauses_start:
            clauses_start.remove(lit_set)
         else:
            sos_strategy.remove(lit_set)
               
   return clauses_start, sos_strategy
            
   
def check_subset(new_clauses, sos_or_start_cl):
   for set1 in new_clauses:
        if set1 not in sos_or_start_cl:
            return False
   return True 
   

#FOR GUIDANCE USED: https://github.com/IVA78/DISKRETNA_MATEMATIKA/blob/main/lab2.cpp
def track_clauses(child, child_parents_dict):
   
   path = deque()
   open = deque([(child, child_parents_dict[child])])
   
   while open:
      child, parents = open.popleft()
      if not (len(parents[0]) == 0 and len(parents[0]) == 0):
         path.append("New clause: {}, Parent clauses: {}".format(child, parents))
      for parent in parents:
         if parent in child_parents_dict:
            open.append((parent, child_parents_dict[parent]))
   
   path.reverse()
   for p in path:
      p = p.replace("frozenset", "")
      p = p.replace("(", "")
      p = p.replace(")", "")
      print(p)
   print("===============")


def resolution_parse_input(file_name, cooking):
   #read lines from file
   file = open(file_name, "r", encoding = "utf-8")
   lines = file.readlines()
   
   #define counters
   lines_length = len(lines)
   count = 0
   
   #define variables for parsing
   clauses_start = [] #list of sets {{¬C,A,B},{¬D,A,B},{¬C,¬B}}
   sos_strategy = [] #negated state and all new clauses_start -> list of sets
   goal_state = False
   child_parents_dict = dict() #child_set:(parent1_set, parent2_set)
   
   #parse and print input data
   for line in lines:
      stripped_line = line.strip().lower()
      if "#" in stripped_line:
         count += 1
         continue
      else:
         count += 1
         if count < lines_length or cooking:
            literals = set()
            if " v " in stripped_line: 
               for el in stripped_line.split(" v "):
                  literals.add(el) 
            else:
               literals.add(stripped_line)
            child_parents_dict[frozenset(literals)] = (frozenset({}), frozenset({}))
            clauses_start.append(literals)
            print(f"{count}. ",stripped_line)
         else:
            goal_state = stripped_line
            literals = set()
            if " v " in stripped_line:
               for el in stripped_line.split(" v "):
                  neg_el = set()
                  neg_el.add(el.replace("~", "") if "~" in el else "~" + el)
                  child_parents_dict[frozenset(neg_el)] = (frozenset({}), frozenset({}))
                  sos_strategy.append(neg_el)
            else:
               neg_el = set()
               neg_el.add(stripped_line.replace("~", "") if "~" in stripped_line else "~" + stripped_line)
               child_parents_dict[frozenset(neg_el)] = (frozenset({}), frozenset({}))
               sos_strategy.append(neg_el)
            
            
            for goal_lit in sos_strategy:
               print(f"{count}. ", end='')
               for lit in goal_lit:
                  print(lit) 
               count+=1
            print("===============")
   
   return clauses_start, sos_strategy, goal_state, child_parents_dict

def plResolution(clauses_start, sos_strategy, goal_state, child_parents_dict): 
   
   #define variables for algorithm
   resolved = dict() #(cl1, cl2): T -> keep track of resolved clauses_start
   new_clauses = [] #new clauses_start -> list of sets
   found_solution = False
   cant_find_solution = False
      
   #ALGORITHM------------------------------------------------------------------------------------------
   c1 = set()
   c2 = set()
   while True:
      #strategy of simplification (remove redundancy and tautology)
      clauses_start, sos_strategy = strategy_of_simplification(clauses_start, sos_strategy)
      
      c1, c2 = selectClauses(clauses_start, sos_strategy, resolved)
      
      
      resolvents = plResolve(c1, c2) #returns list of sets
      
      for cl in resolvents:
         if frozenset(cl) not in child_parents_dict:
            child_parents_dict[frozenset(cl)] = (frozenset(c1), frozenset(c2))
         
         if "NIL" in cl:
            found_solution = True
            break;
         
      new_clauses = resolvents
         
         
      if check_subset(new_clauses, sos_strategy) and check_subset(new_clauses, clauses_start):
         cant_find_solution = True
         break
      
      sos_strategy = sos_strategy + new_clauses
      
      if(found_solution | cant_find_solution): break
   
   #---------------------------------------------------------------------------------------------------
   
   if(found_solution):
      #track clauses
      child = {"NIL"}
      track_clauses(frozenset(child), child_parents_dict)
      
      print(f"[CONCLUSION]: {goal_state} is true")
   
   if(cant_find_solution):
      print(f"[CONCLUSION]: {goal_state} is unknown")        
 
def cooking(clauses_file, commands_file):
   
   print("Constructed with knowledge:")
   
   clauses_start, sos_strategy, goal_state, child_parents_dict = resolution_parse_input(clauses_file, True)

   #read lines from file
   file = open(commands_file, "r", encoding = "utf-8")
   lines = file.readlines()
   
   for line in lines:
      line = line.strip().lower()
      print("\nUser's command: ", line)
      
      if "+" in line:
         command = "+"
         cl, rest = line.split("+")
      if "-" in line:
         command = "-"
         cl, rest = line.split("-")
      if "?" in line:
         command = "?"
         cl, rest = line.split("?")
      
      #parse new clausule
      literals = set()
      if " v " in cl: 
         for el in cl.split(" v "):
            literals.add(el.strip()) 
      else:
         literals.add(cl.strip())
      
      if command == "-":
         if literals in sos_strategy:
            sos_strategy.remove(literals)
         if literals in clauses_start:
            clauses_start.remove(literals)
         print("Removed", cl)
            
      if command == "+":
         clauses_start.append(literals)
         child_parents_dict[frozenset(literals)] = (frozenset({}), frozenset({}))
         print("Added", cl)
         
      if command == "?":
         
         count = 1
         for cl_set in clauses_start:
            print(f"{count}. {cl_set}")
            count += 1
         print("===============")
            
         
         goal_state = cl.strip()
         for literal in literals:
            neg_literal = set()
            neg_literal.add(literal.replace("~", "") if "~" in literal else "~" + literal)
            sos_strategy.append(neg_literal)
            child_parents_dict[frozenset(neg_literal)] = (frozenset({}), frozenset({}))
         
         
         clauses_start_copy = clauses_start.copy()
         plResolution(clauses_start, sos_strategy, goal_state, child_parents_dict)
         sos_strategy = []
         clauses_start = clauses_start_copy

if __name__ == "__main__":
   
   #get arguments
   args = sys.argv
   
   #extract the .txt file name
   if 'resolution' in args:
      index = args.index('resolution')
      file_name = args[index + 1]
      
      #parse input for resolution
      clauses_start, sos_strategy, goal_state, child_parents_dict = resolution_parse_input(file_name, False)
      
      #call resolution function
      plResolution(clauses_start, sos_strategy, goal_state, child_parents_dict)
   
   if 'cooking' in args:
      index = args.index('cooking')
      clauses_file = args[index + 1]
      commands_file = args[index + 2]
      
      #call cooking function
      cooking(clauses_file, commands_file)
   
   