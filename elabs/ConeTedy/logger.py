
from elabs.fundamental.utils import log as LOG

def init():
  LOG.initLogger()

def debug(*args,**kwargs):
  LOG.debug(*args,**kwargs)
  
def error(*args,**kwargs):
  LOG.error(*args,**kwargs)

def info(*args,**kwargs):
  LOG.info(*args,**kwargs)

def warn(*args,**kwargs):
  LOG.warn(*args,**kwargs)


DEBUG = debug
ERROR = error
INFO = info
WARN = warn