import csv
from queue import PriorityQueue
import math
import sys
import copy


#https://www.w3schools.com/python/python_classes.asp
#https://www.youtube.com/watch?v=apACNr7DC_s&list=WL&index=3
class ID3():
   
   tree_model = ()
   x_values_dict = dict()
   
   def fit(self, train_dataset, depth):
      
      #procitaj podatke
      #https://www.geeksforgeeks.org/reading-csv-files-in-python/
      with open(train_dataset, mode ='r') as file:
         csvFile = csv.reader(file)
         cnt = 0;
         #izvuci znacajke 
         x = list()
         #spremi retke za kasnije
         d = dict()
         #spremi moguce vrijednosti za y
         y = set()
         
         cnt_d = 1;
         for lines in csvFile:
            if cnt == 0:
               x = lines
               x.pop(-1) #izbaci y iz znacajki
               cnt += 1
            else : 
               d[cnt_d] = lines
               cnt_d += 1
               y.add(lines[-1])
         
         #print("X: ", x)
         #print("D: ", d)
         #print("y: ", y)
         
      
      #unutarnja funkcija - id3 rekurzivni algoritam
      #https://www.geeksforgeeks.org/python-inner-functions/
      def id3_inner(d, d_parent, x, y, curr_v, depth):
         #print("d: ", d)
         #print("d_parent: ", d_parent)
         #print("x: ", x)
         #print("y: ", y)
         
         #UVJETI ZAUSTAVLJANJA REKURZIVNIH POZIVA
         
         #1) d skup je prazan
         if not d:
            y_dict_parent = dict() #pogledat cu vrijednosti za y i njihov broj u roditeljskom skupu
            for row in d_parent.values():
               #print("row: ", row)
               #print("curr_v: ", curr_v)
               if curr_v != row[0]: continue
               y_value = row[-1]
               if y_value in y_dict_parent:
                  counter = y_dict_parent[y_value]
                  counter += 1
                  y_dict_parent.update({y_value: counter})
               else:
                  y_dict_parent[y_value] = 1
            #print("y_dict_parent: ", y_dict_parent)
            y_argmax = max(y_dict_parent, key=lambda k:(y_dict_parent[k], -ord(k[0:1])))
            #print("d empty: ", y_argmax)
            return y_argmax
         
         #2) x je prazan ili su u d skupu samo uniformne vrijednosti
         y_dict_current = dict() #pogledat cu vrijednosti za y i njihov broj u trenutnom skupu
         y_set_current = set()
         for row in d.values():
            y_value = row[-1]
            y_set_current.add(y_value)
            if y_value in y_dict_current:
               counter = y_dict_current[y_value]
               counter += 1
               y_dict_current.update({y_value: counter})
            else:
               y_dict_current[y_value] = 1
               
         
         #print("y_dict_current: ", y_dict_current)
               
         if not x or len(y_set_current) == 1:
            y_argmax = max(y_dict_current, key=lambda k:(y_dict_current[k], -ord(k[0:1])))
            #print("x empty or y_set uniform: ", y_argmax)
            return y_argmax
         
         
         #PRIPREMA PODATAKA
         x_value_total = dict() #('weather', 'sunny'): 5
         x_value_with_y = dict() # ('weather', 'sunny', 'no'): 3
         x_values = dict() # 'weather': {'cloudy', 'sunny', 'rainy'}
         y_dict = dict() # {'True': 4, 'False': 4}
         y_values_sum = 0 #
         
         for row in d.values():
            
            y_value  = row[-1]
            #print("y_value: ", y_value)
            if y_value in y_dict:
               counter = y_dict[y_value]
               counter += 1
               y_dict.update({y_value: counter})
               y_values_sum += 1
            else:
               y_dict[y_value] = 1
               y_values_sum += 1
            
            cnt = 0
            row_copy = row.copy()
            row_copy.pop(-1)
            for value in row_copy:
               #napuni rjecnike
               #print("x: ", x) 
               #print("cnt: ", cnt)
               
               if (x[cnt], value, y_value) in x_value_with_y:
                  counter = x_value_with_y[(x[cnt], value, y_value)]
                  counter += 1
                  x_value_with_y.update({(x[cnt], value, y_value): counter})
               
               else:
                  x_value_with_y[(x[cnt], value, y_value)] = 1
                  
               if (x[cnt], value) in x_value_total:
                  counter = x_value_total[(x[cnt], value)]
                  counter += 1
                  x_value_total.update({(x[cnt], value): counter})
               else:
                  x_value_total[(x[cnt], value)] = 1
                  
               if x[cnt] in x_values:
                  v_set = x_values[x[cnt]]
                  v_set.add(value)
                  x_values.update({x[cnt]: v_set})
               else:
                  v_set = set()
                  v_set.add(value)
                  x_values[x[cnt]] = v_set
               
               cnt += 1
               
         
         #print("y_dict: ", y_dict)
         #print("y_values_sum: ", y_values_sum)
         #print("x: ",x)
         #print("x_value_with_y: ", x_value_with_y)
         #print("x_value_total: ", x_value_total)
         #print("x_values: ", x_values)
         
         if not ID3.x_values_dict:
            ID3.x_values_dict = x_values
         
         
         #IZRACUN ARGMAXA
         
         #1) E(D)
         e_d = 0
         #print("y_sum: ", y_values_sum)
         for y_value in y_dict:
            e_d = e_d + (y_dict[y_value] / y_values_sum) * math.log2(y_dict[y_value] / y_values_sum)
         e_d = -round(e_d, 4)
         #print("e_d: ", e_d)
         
         #2) IG(x_value)
         ig_dict = dict()
         for x_value in x_values:
            v_sum = 0
            for v_value in x_values[x_value]:
               value_cnt_sum = x_value_total[(x_value, v_value)]
               e_v = 0
               for y in y_dict:
                  if (x_value, v_value, y) in x_value_with_y:
                     value_cnt = x_value_with_y[(x_value, v_value, y)]
                     e_v += value_cnt / value_cnt_sum * math.log2(value_cnt / value_cnt_sum)
               if e_v != 0: e_v = -e_v
               e_v = round(e_v, 4)
               #print("e_v: ", e_v)
               v_sum += value_cnt_sum/ y_values_sum * e_v
            
            ig_dict[x_value] = round(e_d - v_sum, 4)
         
         #print("ig_dict: ", ig_dict)
         x_argmax = max(ig_dict, key=lambda k:(ig_dict[k], -ord(k[0:1])))
         #print("x_argmax: ", x_argmax)
         
         
         #NOVI REKURZIVNI POZIV
         subtrees=[]
         for v in sorted(x_values[x_argmax]):
            
            #print("d: ", d)
            index_of_x = x.index(x_argmax)
            #print("x: ", x)
            #print("index_of_x: ", index_of_x)
            #print("v: ", v)
            #odaberi nove retke
            d_new = dict()
            d_copy = copy.deepcopy(d)
            for k, row in d_copy.items():
               #print("row: ", row)
               if v in row:
                  indexes_of_v = [index for index, val in enumerate(row) if val == v]
                  #print("indexes_of_v: ", indexes_of_v)
                  for index_of_v in indexes_of_v:
                     if index_of_v == index_of_x:
                     
                        #print("row.index(v): ", row.index(v))
                        #print("row: ", row)
                        #row_copy = row.copy()
                        #row.pop(index_of_x)
                        d_new[k] = row
                        d_new[k].pop(index_of_x)
            #print("d_new: ", d_new)
            
            #kopiraj x i ukloni x_argmax
            x_new = copy.deepcopy(x)
            x_new.remove(x_argmax)
            
            #print("d_end: ", d)
            #novi poziv
            
            if depth is not None and int(depth) == 0:
               #print("y_dict_current: ", y_dict_current)
               y_argmax = max(y_dict_current, key=lambda k:(y_dict_current[k], -ord(k[0:1])))
               #print("x empty or y_set uniform: ", y_argmax)
               return y_argmax
               
            
            if depth is None:
               t = id3_inner(d_new, d, x_new, y, v, depth)
            else:
               t = id3_inner(d_new, d, x_new, y, v, int(depth) - 1)
            subtrees.append((v, t))
         
         return x_argmax, subtrees
               
         
            
      def recursive_print(subtree, depth, before):
         if isinstance(subtree, tuple): #uvijek imam tupple, osim kad dodjem do lista tj.same oznake klase (yes, no)
           (one, two) = subtree #one je u ovom slucaju vrijednost "cvora", a two je pripadajuca lista/tupple
           for list_el in two: #za svaku vrijednost liste/tupple
            first, second = (list_el)
            new_before = f" {before} {depth}:{one}={first} ".strip()
            recursive_print(second, depth+1, new_before)
         else: #dosla sam do lista, ispisi oznaku klase (subtree) i i sve "ispred" nje
            print(before, subtree)
            
            
      subtrees = id3_inner(d,d,x, y, "", depth)
      #print("\nresult: ", subtrees)
      print("[BRANCHES]:")
      recursive_print(subtrees, 1, "")
         
      ID3.tree_model = subtrees   
         
      
      
      
      
   def predict(self, test_dataset):
      #print("PREDICTING: ")
      #print(ID3.tree_model, "\n")
      
      with open(test_dataset, mode ='r')as file:
         csvFile = csv.reader(file)
         cnt = 0;
         #izvuci znacajke 
         x = list()
         #spremi retke za kasnije
         d = dict()
         #spremi moguce vrijednosti za y
         y = list()
         
         #dohvati vrijednosti znacajki u stablu
         x_values_dict = ID3.x_values_dict
         
         cnt_d = 1;
         for lines in csvFile:
            if cnt == 0:
               x = lines
               x.pop(-1) #izbaci y iz znacajki
               cnt += 1
                  
            else : 
               y.append(lines[-1])
               lines.pop(-1)
               d[cnt_d] = lines
               cnt_d += 1
               
               
                  
               
         
         #print("X: ", x)
         #print("D: ", d)
         #print("y: ", y, "\n")
         #print("x_values_dict: ", x_values_dict)
         
         def find_majority(subtree, before):
               
            result = []
            if isinstance(subtree, tuple): #uvijek imam tupple, osim kad dodjem do lista tj.same oznake klase (yes, no)
               (one, two) = subtree #one je u ovom slucaju vrijednost "cvora", a two je pripadajuca lista/tupple
               for list_el in two: #za svaku vrijednost liste/tupple
                  first, second = (list_el)
                  #print("first: ", first)
                  #print("second: ", second)
                  new_before = f" {before} {one} {first} ".strip()
                  result.append(find_majority(second, new_before))
            else: #dosla sam do lista, ispisi oznaku klase (subtree) i i sve "ispred" nje
               result.append(before + ' ' + subtree)
               #print(before, subtree)
            
            return result
      
         
         def recursive_check(row, x_copy, tree_copy):
            predictions_to_return = ""
            #print("row: ", row)
            #print("tree_copy: ", tree_copy)
         
            if isinstance(tree_copy, tuple):
               (one, two) = tree_copy
               #print("one: ", one)
               #print("two: ", two)
               #print("two_atr: ", two[0])
               
               index_of_x = x_copy.index(one)
               #print("value in row on index: ", row[index_of_x])
               value = row[index_of_x]
               for list_el in two:
                  first, second = (list_el)
                  if(first == value):
                     predictions_to_return += recursive_check(row, x_copy, second)
                  
                  #print("x_values_dict: ", x_values_dict)
                  if value not in x_values_dict[one]:
                     #return majority of the current node
                     #print("for majority: ",tree_copy)
                     result = find_majority(tree_copy, "")
                     majority_dict = dict()
                     #print("rez: ", result)
                     for r in result:
                        for v in r:
                           v_splitted = v.strip().split(' ')
                           #print("type: ", type(v))
                           label = v_splitted[-1]
                           #print(r, end=' ')
                           #print(f"label:{label}|")
                           if label in majority_dict:
                              counter = majority_dict[label]
                              counter += 1
                              majority_dict.update({label: counter})
                           else:
                              majority_dict[label] = 0
                     
                     most_common_label = max(majority_dict, key=lambda k:(majority_dict[k], -ord(k[0:1])))
                     predictions_to_return += most_common_label + ' '
                     return predictions_to_return
                     
            else:
               predictions_to_return += tree_copy + ' '
               #print(tree_copy, end=' ')
            return predictions_to_return
          
         
            
         print("[PREDICTIONS]:", end=' ')
         predictions = ""
         #za svaki redak
         for row in d.values():
            #print("row: ", row)
            #kopiraj model - mijenjat cemo ga kroz rekurzivan obilazak?
            tree_copy = tuple(ID3.tree_model)
            #obidji stablo za trenutni redak
            x_copy = x.copy()
            predictions += recursive_check(row, x_copy, tree_copy)
            
         print(predictions.strip())
         
         #ACCURACY AND ACCURACY MATRIX
         predictions_set = set(predictions.strip().split(" "))
         #print("predictions_set: ", predictions_set)
         
         
         confusion_dict = dict()
         y_set = set(y)
         for value1 in sorted(y_set):
            for value2 in sorted(y_set):
               confusion_dict[value1, value2] = 0
            
         
         #FIX THIS: treba ici po predikcijama i unutra petlja za y_set
         cnt = 0
         correct_sum = 0
         #print("y: ", y)
         #print("predictions: ", predictions)
         
         for y_value in y:
            
            #print(f"y_value:{y_value}| ")
            y_prediction = predictions.strip().split(" ")[cnt]
            #print(f"y_prediction:{y_prediction}| ")
            counter = confusion_dict[(y_value, y_prediction)]
            counter += 1
            confusion_dict.update({(y_value, y_prediction): counter})
            if y_value == y_prediction:
               #print(f"y_value:{y_value}| ")
               #print(f"y_prediction:{y_prediction}| ")
               correct_sum += 1
            cnt += 1
         
         #print("conf_len: ", len(confusion_dict))
             
           
         accuracy = correct_sum / len(y)
         print("[ACCURACY]:", f"{accuracy:.5f}")
         #print("correct_sum: ", correct_sum)
         #print("len(y): ", len(y))
         
         
         #https://www.geeksforgeeks.org/how-to-sort-a-set-of-values-in-python/
         y_sorted = sorted(y_set)
         print("[CONFUSION_MATRIX]:")
         for value1 in y_sorted:
            for value2 in y_sorted:
               print(confusion_dict[value1, value2], end=' ')
            print()
         
            


#https://realpython.com/python-main-function/
def main():
   
   
   train_dataset = sys.argv[1]
   test_dataset = sys.argv[2]
    
   depth = None
   if len(sys.argv) > 3:
      depth = sys.argv[3]
    
   #print(train_dataset)
   #print(test_dataset)
   
   model = ID3()
   model.fit(train_dataset, depth)
   model.predict(test_dataset)
    
if __name__ == "__main__":
    main()