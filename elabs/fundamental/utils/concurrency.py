#coding:utf-8
from copy import  deepcopy
from multiprocessing import Process,Queue
from threading import Thread


def task_split(taskes,num= 5):
  """
    ([a,b,c,d,e,f,g] , 3) => [ (a,b,c),(e,f,g) ]
  """
  ss = []
  groups = []
  taskes = deepcopy(taskes)
  while taskes:
    ss.append(taskes.pop(0))
    if len(ss) >= num:
      groups.append(ss)
      ss = []
  if ss:
    groups.append(ss)
  return groups

def multiprocess_task_split(func,params,task_list,n_core,concls=Process):
  num_per_core = int( len(task_list) / n_core )
  groups = task_split(task_list,num_per_core)
  process_list = []
  q = Queue()
  
  def run(group,q):
    for task in group:
      res = func(task,params)
      q.put(res)
      
    print '--'*20
      
  for group in groups:
    p = concls(target=run,args=(group,q))
    p.start()
    # p.join()
    process_list.append(p)
    
  for p in process_list:
    p.join()
  res = []
  # print 'qsize:',q.qsize()
  while q.qsize():
    data = q.get()
    res.append(data)
    
  return res

def test_multipleprocess():
  def my_func(task,params):
    print task , params
    return task
  
  data = multiprocess_task_split(my_func,[100,101],range(10),3)
  print data
  
if __name__ == '__main__':
  test_multipleprocess()