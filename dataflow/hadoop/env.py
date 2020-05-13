import os
import re


# hadoop environments
__HADOOP_ENV = {}

def initialize(
    home = None,
    hadoop = None,
    streaming = None,
):
    global __HADOOP_ENV
    __HADOOP_ENV = {}

    # hadoop home
    if home is None:
        home = os.getenv('HADOOP_HOME', None)
        if home is None: return
    __HADOOP_ENV['home'] = home


    # hadoop execute
    if hadoop is None:
        hadoop = os.path.join(home, 'bin', 'hadoop')
    __HADOOP_ENV['hadoop'] = hadoop



    # hadoop streaming
    if streaming is None:
        pattern = re.compile('^hadoop-streaming(-[0-9|.]+)?\.jar$')
        for root, dirs, files in os.walk(home):
            for file in files:
                m = pattern.match(file)
                if m is None: continue
                streaming = os.path.join(root, file)
                break
        if streaming is None: return
    __HADOOP_ENV['streaming'] = streaming



def getenv(name, default=None): return __HADOOP_ENV.get(name, default)

def _getenv(name):
    if name not in __HADOOP_ENV: raise Exception('Hadoop environemnt variable {} not exist'.format(name))
    return __HADOOP_ENV.get(name)


# initialize automatically
initialize()