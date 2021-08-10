#coding:utf-8

import sys,os,os.path,traceback,time,datetime
import json
import toml
import fire
import pymongo
from elabs.ConeTedy.model import Project
from elabs.fundamental.utils.importutils import import_function
from elabs.ConeTedy.context import Context
from elabs.ConeTedy.logger import INFO,DEBUG,WARN,ERROR,init as init_log
from elabs.ConeTedy import logger

from elabs.ConeTedy import model
from elabs.fundamental.utils.useful import make_dir

PWD = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(PWD,'tedy-settings.toml')
settings = toml.load(file)

def init_database():
  conn = pymongo.MongoClient(**settings['NoSQL'])
  return conn['ConeTedy']

database = init_database()
model.set_database(database)

init_log()
#---------------------------------------

def run(prj_id,batch_task_id):
  """ 运行指定的task
  """
  INFO('batch task run:{}'.format(batch_task_id,prj_id))

  batch_task = model.BatchTask.get(batch_task_id = batch_task_id , prj_id = prj_id )
  if not batch_task:
    ERROR('batch task not found!',batch_task_id)
    return

  # worker = model.Worker.get(batch_task_id=batch_task_id)
  # if not worker:
  #   worker = model.Worker()
  # worker.batch_task_id = batch_task_id
  # worker.pid = os.getpid()
  # worker.save()

  prj = Project.get(prj_id = batch_task.prj_id)
  
  path = os.path.join(settings['repo_dir'],batch_task.prj_id)
  sys.path.append(path)
  path = os.path.join(settings['repo_dir'], batch_task.prj_id, 'cone-project.toml')
  prj.configs = toml.load(open(path))
  imp_entry = prj.configs.get('task_exec', {}).get('entry')  # 加载运行触发入口
  if not imp_entry:
    return
  fx = import_function(imp_entry)
  #
  for task_id in batch_task.task_list:
    task = model.Task.get(prj_id = batch_task.prj_id,task_id = task_id)
    ctx = Context()
    ctx.task = task
    ctx.project = prj
    # ctx.worker = worker
    ctx.logger = logger
    task.start_time = datetime.datetime.now()
    task.status = 'running'
    task.save()
    fx(ctx)  # main.computating(ctx)
    task.end_time = datetime.datetime.now()
    task.save()


def project_deploy(prj_id):
  """执行部署项目代码之后执行事件"""

  INFO('>> project_deploy:{}'.format(prj_id))

  # prj = Project.get(prj_id=prj_id)
  # if not prj:
  #   return

  path = os.path.join(settings['repo_dir'],prj_id)
  sys.path.append(path)

  path = os.path.join(settings['repo_dir'], prj_id, 'cone-project.toml')

  configs = toml.load(open(path))
  imp_entry = configs.get('project_deploy',{}).get('entry')  # 加载运行触发入口
  if not imp_entry:
    return

  INFO('import function:',imp_entry)
  fx = import_function(imp_entry)
  #
  prj = Project()
  prj.dir = path
  path = os.path.join(settings['data_dir'],prj_id)
  if not os.path.exists(path):
    # os.mkdir(path)
    make_dir(path)
  prj.data_dir = path

  ctx = Context()
  ctx.project = prj
  ctx.logger = logger
  fx(ctx)  # main.project_deploy(ctx)


def data_deploy(prj_id):
  """项目数据更新或部署"""

  INFO('>> data_deploy:{}'.format(prj_id))

  prj = Project.get(prj_id=prj_id)
  if not prj:
    ERROR("Project Not Register.",prj_id)
    return
  
  path = os.path.join(settings['repo_dir'], prj_id)
  prj.dir = path
  path = os.path.join(settings['data_dir'], prj_id)
  if not os.path.exists(path):
    make_dir(path)
  prj.data_dir = path
  
  path = os.path.join(settings['repo_dir'], prj_id, 'cone-project.toml')
  sys.path.append(prj.dir)

  prj.configs = toml.load(open(path))
  imp_entry = prj.configs.get('data_deploy',{}).get('entry')  # 加载运行触发入口
  if not imp_entry:
    return
  fx = import_function(imp_entry)
  #
  ctx = Context()
  ctx.project = prj
  ctx.logger = logger
  fx(ctx)  # main.project_deploy(ctx)

if __name__ == '__main__':
  fire.Fire()

"""
/home/dcp/anaconda3/bin/python -m TedyNode.tedyworker project_deploy DemoPhoenix
"""