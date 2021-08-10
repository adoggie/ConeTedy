#coding:utf-8

from elabs.fundamental.nosql.model import Model,_set_database


class Task(Model):
  def __init__(self):
    Model.__init__(self)
    self.prj_id = ''
    self.task_id = ''
    self.start_time = ''
    self.end_time = ''
    self.data = {}
    self.status = 'idle' # idle,running,finished

class BatchTask(Model):
  """批次任务集合"""
  def __init__(self):
    Model.__init__(self)
    self.prj_id = ''
    self.batch_task_id = ''
    self.task_list = []
    self.data = {}
    self.node = ''

class Project(Model):
  def __init__(self):
    Model.__init__(self)
    self.prj_id = ''
    self.configs = {}

    self.dir = ''   # 代码目录
    self.data_dir = '' # 数据目录

class Worker(Model):
  def __init__(self):
    Model.__init__(self)
    self.prj_id = ''
    self.batch_task_id = ''
    self.status = ''
    self.data_dir = ''
    self.pid = 0


class Node(Model):
  def __init__(self):
    Model.__init__(self)
    self.node_id = ''
    self.ip = ''
    self.rpc = ''
    self.configs = {}   # with cone-project.toml
    self.repo_dir = ''  # 当前节点的仓库目录  /opt/conetedy/repo/Demo1/
    self.data_dir = ''  # 当前节点的数据目录  /opt/conetedy/data/Demo1/


var_locals = locals()

def set_database(database):
    _set_database(var_locals,database)

init_database = set_database


