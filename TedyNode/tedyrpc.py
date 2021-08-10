#coding:utf-8

"""
pip install tinyrc
"""

import sys,os,os.path,traceback,time,datetime
import json
import toml
import fire
import pymongo
import gevent
import gevent.pywsgi
import gevent.queue
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher

from elabs.ConeTedy.model import Project,Task,Worker,BatchTask
from elabs.ConeTedy import model
from elabs.ConeTedy.logger import INFO,DEBUG,WARN,ERROR,init as init_log

PWD = os.path.dirname(os.path.abspath(__file__))
dispatcher = RPCDispatcher()

class TedyServer(object):
  """调度上下文"""
  def __init__(self):
    self.configs = {} #  with cone-project.toml
    self.nosql = None

  def init(self):
    path = os.path.join(PWD,'tedy-settings.toml')
    self.configs = toml.load(open(path))
    self.nosql = pymongo.MongoClient(**self.configs['NoSQL'])
    return self

file = os.path.join(PWD,'tedy-settings.toml')
settings = toml.load(file)

def init_database():

  conn = pymongo.MongoClient(**settings['NoSQL'])
  return conn['ConeTedy']

database = init_database()
model.set_database(database)

init_log()
#---------------------------------------

tedy= TedyServer().init()

def run_server():
  transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
  # start wsgi server as a background-greenlet
  wsgi_server = gevent.pywsgi.WSGIServer(('', settings['rpc_port']), transport.handle)
  gevent.spawn(wsgi_server.serve_forever)
  rpc_server = RPCServerGreenlets(transport, JSONRPCProtocol(), dispatcher)
  # in the main greenlet, run our rpc_server
  INFO("TedyRpcServer STARTED..",settings['rpc_port'])
  rpc_server.serve_forever()

@dispatcher.public
def project_run( prj_id):
  prj = Project.get(prj_id=prj_id)
  if not prj:
    WARN('project not existed!', prj_id)
    return
  
  rs = model.BatchTask.find(prj_id = prj_id, node = settings['name'])
  for btask in rs:
    batch_task_run(task = btask)
    
  

@dispatcher.public
def data_deploy(prj_id):
  """项目数据部署或同步请求"""

  prj = Project.get(prj_id=prj_id)
  if not prj:
    WARN('project not existed!', prj_id)
    return
  
  pattern = "flock -xn /tmp/data-deploy-{prj_id}.lock -c 'cd {pwd}/..; python -m TedyNode.tedyworker data_deploy {prj_id}' >> data-deploy-{prj_id}.log & "
  pattern = "flock -xn /tmp/data-deploy-{prj_id}.lock -c 'cd {pwd}/..; python -m TedyNode.tedyworker data_deploy {prj_id}' & "
  cmd = pattern.format( prj_id=prj_id, pwd=PWD)
  DEBUG(cmd)
  os.system(cmd)

@dispatcher.public
def project_deploy(prj_id):
  """ admin 完成项目代码远程部署之后触发"""
  # prj = Project.get(prj_id = prj_id)
  # if not prj:
  #   WARN('project not existed!',prj_id)
  #   return
  pattern = "flock -xn /tmp/project-deploy-{prj_id}.lock -c 'cd {pwd}/..; {python} -m TedyNode.tedyworker project_deploy {prj_id}' >> project-deploy-{prj_id}.log & "
  pattern = "flock -xn /tmp/project-deploy-{prj_id}.lock -c 'cd {pwd}/..; {python} -m TedyNode.tedyworker project_deploy {prj_id}' &  "
  cmd = pattern.format( prj_id =prj_id,pwd = PWD, python= settings['python'])
  DEBUG(cmd)
  os.system(cmd)


# @dispatcher.public
def batch_task_run(batch_task_id ='' ,task = None):
  """调度批次任务加载worker进程"""
  if not task:
    task = BatchTask.get(batch_task_id = batch_task_id)
  if not task:
    WARN('task not existed!', batch_task_id)
    return
  pattern = "flock -xn /tmp/batch_task_{task_id}.lock -c 'cd {pwd}/..; {python} -m TedyNode.tedyworker run {task_id}' >> batch_task_{task_id}.log & "
  pattern = "flock -xn /tmp/batch_task_{task_id}.lock -c 'cd {pwd}/..; {python} -m TedyNode.tedyworker run {prj_id} {task_id}'  "
  cmd = pattern.format(
    task_id=task.batch_task_id, prj_id = task.prj_id, pwd=PWD, python= settings['python']
  )
  DEBUG(cmd)
  os.system(cmd)


# @dispatcher.public
def batch_task_stop(batch_task_id):
  """终止任务运行 """
  task = BatchTask.get(batch_task_id = batch_task_id)
  if not task:
    WARN('task not existed!', batch_task_id)
    return

  cmd = "pkill -f 'TedyNode.tedyworker run {prj_id} {task_id}'".format( task_id=batch_task_id,prj_id = task.prj_id)
  DEBUG(cmd)
  os.system(cmd)

#
if __name__ == '__main__':
  run_server()