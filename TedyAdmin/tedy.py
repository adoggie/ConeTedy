#coding:utf-8


import sys,os,os.path,traceback,time,datetime
import copy
import json
import toml
import fire

PWD = os.path.dirname(os.path.abspath(__file__))

def tedy_settings():
  file = os.path.join(PWD, 'tedy-settings.toml')
  data = toml.load( open(file))
  nodes = {}
  for n in data['nodes']:
    nodes[n['name']] = n
  data['nodes'] = nodes
  return data
