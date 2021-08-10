#coding:utf-8


class Task(object):
  """调度上下文"""
  def __init__(self):
    self.configs = {} #  with cone-project.toml
    self.model = None

class TaskQueue(object):
  pass

class TaskResult(object):
  pass