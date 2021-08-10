#coding:utf-8

from elabs.ConeTedy.node import Node
from elabs.ConeTedy.model import Project

class Context(object):
  """调度上下文"""
  def __init__(self):
    self.configs = {} #  with cone-project.toml
    self.task =  None
    self.data = None
    self.node  = None  # 执行主机节点
    self.worker = None # 执行工作进程
    self.project :Project =  None




if __name__ == '__main__':
  print(Context().node)