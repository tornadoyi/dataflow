from inspect import isfunction, ismethoddescriptor
from functools import partial
from pyarrow import hdfs




#  wrapper hdfs members
def connect(*args, **kwargs): return hdfs.connect(*args, **kwargs)



# import all member functions from hdfs.HadoopFileSystem
def __wrapper(f):
    def call(f, *args, **kwargs):
        r = hdfs.connect()
        return f(r, *args, **kwargs)

    return partial(call, f)

for k in dir(hdfs.HadoopFileSystem):
    v = getattr(hdfs.HadoopFileSystem, k)
    if k.startswith('_') or \
        k in globals() or \
        (not isfunction(v) and not ismethoddescriptor(v)): continue
    globals()[k] = __wrapper(v)




