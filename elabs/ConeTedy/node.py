#coding:utf-8


class Node(object):
  """调度上下文"""
  def __init__(self):
    self.configs = {} #  with cone-project.toml

  @property
  def repo_dir(self):
    # 当前节点的仓库目录  /opt/conetedy/repo/Demo1/
    pass

  @property
  def data_dir(self):
    # 当前节点的数据目录  /opt/conetedy/data/Demo1/
    return