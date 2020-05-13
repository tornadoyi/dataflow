import json
import redis
from inspect import isfunction
from functools import partial


def __wrapper(f):
    def call(f, host, port, *args, **kwargs):
        r = redis.Redis(host=host, port=port, db=0)
        return f(r, *args, **kwargs)

    return partial(call, f)



# import all member functions from redis.Redis
for k, v in redis.Redis.__dict__.items():
    if not isfunction(v): continue
    globals()[k] = __wrapper(v)



# override functions
def pipeline(host, port, transaction=True, shard_hint=None, **connect_kwargs):
    rds = redis.Redis(host=host, port=port, db=0, **connect_kwargs)
    return rds.pipeline(transaction, shard_hint)



def get_jsons(host, port, *keys):
    vs = mget(host, port, *keys)
    return [None if v is None else json.loads(v) for v in vs]


def get_json(host, port, key):
    return get_jsons(host, port, key)[0]


def set_jsons(host, port, **kwargs):
    '''
    :param **kwargs: k1-v2, k2-v2, ...
    '''
    jdict = {}
    for k, v in kwargs.items():
        jstr = json.dumps(v, ensure_ascii=False)
        jstr = jstr.replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
        jdict[k] = jstr

    return mset(host, port, jdict)


def set_json(host, port, key, value):
    '''
    :param key: string
    :param value: dict or array
    :return:
    '''
    return set_jsons(host, port, **{key: value})
