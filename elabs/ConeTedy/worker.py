#coding:utf-8


class Worker(object):
  """调度上下文"""
  def __init__(self):
    self.configs = {} #  with cone-project.toml

  @property
  def node(self):
    #
    pass

  @property
  def id(self):
    pass

  @property
  def data_dir(self):
    # $node_data/$project/$work-id
    # /opt/conetedy/worker/Project1/wrk-001
    return