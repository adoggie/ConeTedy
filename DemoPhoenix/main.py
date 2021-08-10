#coding:utf-8

import time
from elabs.ConeTedy.context import Context
from elabs.ConeTedy.task import TaskQueue,TaskResult
from elabs.ConeTedy.model import BatchTask
from elabs.ConeTedy.logger import INFO,DEBUG,WARN,ERROR,init as init_log

init_log()
# remote
def project_deploy(ctx : Context)->str:
  """项目代码部署触发"""
  INFO("my project deployed!")
  
  INFO(ctx.project.data_dir,ctx.project.dir)

# remote
def data_deploy(ctx: Context) :
  """数据部署触发"""
  INFO(">> data_deploy ..")
  INFO(">> pulling data from database..")

# local
def result_combine(ctx: Context):
  """计算结果聚合"""
  pass

# local
def task_split(ctx: Context) -> list:
  """任务切割"""
  return range(100,105)

# remote
def computating(ctx : Context) :
  INFO(">> computing...")
  DEBUG('DATA:',ctx.task,ctx.task.data)
  DEBUG('SLEEP..')
  time.sleep(2)
  
  return None


if __name__ == '__main__':
  data_deploy(None)

