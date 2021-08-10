#coding:utf-8

import os,os.path


def vi_edit(name):
  vi = '/usr/bin/vim'
  if not os.path.exists('/usr/bin/vim'):
    vi = '/usr/bin/vi'
  fn = name
  os.system('{} {}'.format(vi,fn))