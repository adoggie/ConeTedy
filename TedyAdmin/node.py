#coding:utf-8
import sys,os,os.path,traceback,time,datetime
import copy
import json
import toml
import fire

from .tedy import tedy_settings
PWD = os.path.dirname(os.path.abspath(__file__))

def install(node=''):
  """init node and install TedyNode"""
  settings = tedy_settings()
  nodes = settings['nodes'].keys()
  if node:
    nodes=[node]
  
  prj_dir = os.path.join(PWD,'../TedyNode')
  for name in nodes:
    node = settings['nodes'][name]

    settings_file = os.path.join(prj_dir,'tedy-settings.toml')
    data = node
    data['NoSQL'] = settings['NoSQL']
    toml.dump(data,open(settings_file,'w'))

    cmd = "rsync -av -e 'ssh -p {port} -o StrictHostKeyChecking=no ' {prj_dir} {user}@{ip}:{repo}". \
      format(prj_dir=prj_dir, user=node['user'], port=node['port'], ip=node['ip'], repo=node['node_dir'])
    print(cmd)
    os.system(cmd)

    prj_dir = os.path.join(PWD, '../elabs')
    cmd = "rsync -av -e 'ssh -p {port} -o StrictHostKeyChecking=no ' {prj_dir} {user}@{ip}:{repo}". \
      format(prj_dir=prj_dir, user=node['user'], port=node['port'], ip=node['ip'], repo=node['node_dir'])
    print(cmd)
    os.system(cmd)


__all__ = ('install',)

if __name__ == '__main__':
  fire.Fire()