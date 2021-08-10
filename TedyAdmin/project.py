#coding:utf-8

import sys,os,os.path,traceback,time,datetime
import copy
import json
import toml
import fire
import pymongo

from elabs.ConeTedy import logger
from elabs.ConeTedy import model

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from tinyrpc import RPCClient

from .tedy import tedy_settings

from elabs.fundamental.utils.importutils import import_function
from elabs.ConeTedy.context import Context
from elabs.ConeTedy.logger import *
from elabs.ConeTedy import model
from elabs.fundamental.utils.useful import make_dir



PWD = os.path.dirname(os.path.abspath(__file__))

def init_database():
  settings = tedy_settings()
  conn = pymongo.MongoClient(**settings['NoSQL'])
  return conn['ConeTedy']

database = init_database()
model.set_database(database)

def status(exc_id):
  pass


def init(prj_id):
  settings = tedy_settings()
  repo_dir = settings['default']['repo_dir']

  prj_dir = os.path.join(repo_dir, prj_id)
  if not os.path.exists(prj_dir):
    logger.error("Project not existed!", prj_dir)
    return

  path = prj_dir
  sys.path.append(path)
  
  path = os.path.join(prj_dir, 'cone-project.toml')
  configs = toml.load(open(path))

  prj = model.Project.get(prj_id = prj_id)
  if not prj:
    prj = model.Project()
  prj.prj_id = prj_id
  prj.configs = configs
  prj.save()
  
  INFO('Project Init Okay!')

def task_split(prj_id):
  settings = tedy_settings()
  repo_dir = settings['default']['repo_dir']

  prj_dir = os.path.join(repo_dir, prj_id)
  if not os.path.exists(prj_dir):
    logger.error("Project not existed!", prj_dir)
    return

  path = prj_dir
  sys.path.append(prj_dir)
  
  path = os.path.join(path,'cone-project.toml')
  configs = toml.load(open(path))
  imp_entry = configs.get('task_split', {}).get('entry')  # 加载运行触发入口
  if not imp_entry:
    return
  fx = import_function(imp_entry)
  #
  model.Task.collection().delete_many({'prj_id': prj_id})
  prj = model.Project.get(prj_id = prj_id)
  if not prj:
    logger.error("Project UnInited!", prj_id)
    return
  ctx = Context()
  ctx.project = prj
  task_list = fx(ctx)  # main.task_split(ctx) 项目任务切割

  result_tasks = []
  for n,d in enumerate(task_list):
    task = model.Task.get(prj_id = prj_id,task_id = n)
    if not task:
      task = model.Task()
    task.data = d
    task.task_id = n
    task.prj_id = prj_id
    result_tasks.append(task)
    task.save()

  # 根据 node 的worker数量 组合分配 task到不同的worker
  aval_workers = [] # { node:[ , ]
  for node in configs['nodes']:
    for w in range(node['workers']):
      aval_workers.append( [w,node['name'],[ ] ] ) # ( [0,'node1',[ ] ],[1,'node1', [ ] ], .. )

  inc = 0
  while result_tasks:
    aval_workers[inc][2].append( result_tasks[0])
    inc+=1
    if inc >= len(aval_workers):
      inc = 0

    del result_tasks[0]

  # model.BatchTask
  model.BatchTask.collection().delete_many({'prj_id':prj_id})
  
  # print(aval_workers)
  for n,w in enumerate(aval_workers):
    btask = model.BatchTask()
    btask.prj_id = prj_id
    btask.batch_task_id = n
    
    btask.task_list =  [* map(lambda t:t.task_id, w[2]) ] #  多个任务编号  【1，2，3]
    btask.node = w[1]
    btask.save()
  
  INFO('Workers:',len(aval_workers),' Taskes:',len(task_list))
  INFO('Project Task Split Okay!')

def deploy( prj_id ):
  """部署指定项目到集群
    打包拷贝项目文件到计算节点
  """
  settings = tedy_settings()
  repo_dir = settings['default']['repo_dir']
  
  prj_dir = os.path.join(repo_dir,prj_id)
  if not os.path.exists(prj_dir):
    logger.error("Project not existed!",prj_dir)
    return

  cfg_file = os.path.join(prj_dir,'cone-project.toml')
  cfgs = toml.load( open(cfg_file))
  
  for node in cfgs['nodes']:
    _nod = settings['nodes'].get(node['name'])
    node.update(**_nod)
  
    cmd = "rsync -av -e 'ssh -p {port} -o StrictHostKeyChecking=no ' {prj_dir} {user}@{ip}:{repo}".\
      format(prj_dir=prj_dir,user= node['user'],port=node['port'],ip=node['ip'],repo = node['repo_dir'])
    print(cmd )
    os.system(cmd)
  
  # notify node
  rpc_client = RPCClient(JSONRPCProtocol(),HttpPostClientTransport('http://{ip}:{rpc_port}/'.format(ip=node['ip'],rpc_port=node['rpc_port'])))
  remote_server = rpc_client.get_proxy()
  try:
    remote_server.project_deploy(prj_id)
  except:
    traceback.print_exc()

def data_deploy(prj_id):
  settings = tedy_settings()
  
  repo_dir = settings['default']['repo_dir']
  prj_dir = os.path.join(repo_dir, prj_id)
  if not os.path.exists(prj_dir):
    logger.error("Project not existed!", prj_dir)
    return
  
  cfg_file = os.path.join(prj_dir, 'cone-project.toml')
  # DEBUG(cfg_file)
  cfgs = toml.load(open(cfg_file))
  
  for node in cfgs['nodes']:
    _nod = settings['nodes'].get(node['name'])
    node.update(**_nod)

    # notify node
    rpc_client = RPCClient(JSONRPCProtocol(), HttpPostClientTransport(
      'http://{ip}:{rpc_port}/'.format(ip=node['ip'], rpc_port=node['rpc_port'])))
    remote_server = rpc_client.get_proxy()
    remote_server.data_deploy(prj_id)


def run(prj_id):
  settings = tedy_settings()
  
  repo_dir = settings['default']['repo_dir']
  prj_dir = os.path.join(repo_dir, prj_id)
  if not os.path.exists(prj_dir):
    logger.error("Project not existed!", prj_dir)
    return
  
  cfg_file = os.path.join(prj_dir, 'cone-project.toml')
  # DEBUG(cfg_file)
  cfgs = toml.load(open(cfg_file))
  
  for node in cfgs['nodes']:
    _nod = settings['nodes'].get(node['name'])
    node.update(**_nod)
    
    # notify node
    rpc_client = RPCClient(JSONRPCProtocol(), HttpPostClientTransport(
      'http://{ip}:{rpc_port}/'.format(ip=node['ip'], rpc_port=node['rpc_port'])))
    remote_server = rpc_client.get_proxy()
    remote_server.project_run(prj_id)



def list():
  """ list all projects in registry."""
  prj_list = model.Project.find()
  for prj in prj_list:
    print(prj.prj_id)
    
if __name__ == '__main__':
  fire.Fire()
  # deploy('DemoPhoenix')
  # task_split('DemoPhoenix')
  # init('DemoPhoenix')
  