import os
import copy
from collections import OrderedDict
import logging
import yaml

from easydict import EasyDict as edict



# system configurations
CFG_DATA_PIPE_PATH = os.path.expanduser('~/.dataflow')


CFG_LOG = edict(
    LOG_FORMAT = '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d]: %(message)s',
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S',
    LEVEL = logging.INFO,
    DEFAULT_HANDLER = {
        'name': 'RotatingFileHandler',
        'maxBytes': 10 * 1024 * 1024,   # 10 MB
        'backupCount': 30,
        'encoding': 'utf-8'
    }
)




def load(file, default=None):
    # check
    if not os.path.isfile(file): return default

    # load config from file system
    with open(file, 'r') as f:
        fs_cfg = yaml.load(f, Loader=yaml.FullLoader)

    return Config(fs_cfg)



def save(file, config):
    # create directory
    file_dir = os.path.dirname(file)
    os.makedirs(file_dir, exist_ok=True)

    # remove old file
    if os.path.isfile(file): os.remove(file)

    # save
    with open(file, 'w') as f:
        yaml.dump(config, f, allow_unicode=True)



class Config(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(OrderedDict, self).__init__(*args, **kwargs)
        self.__merge__(*args, **kwargs)

    def __str__(self): return yaml.dump(self)

    def __repr__(self): return self.__str__()

    def __getattr__(self, item):
        return OrderedDict.get(self, item, None)

    def __setattr__(self, key, value):
        OrderedDict.__setitem__(self, key, value)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        d = copy.deepcopy(OrderedDict(self))
        return type(self)(**d)

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        for (k, v) in state.items():
            self.__setitem__(k, v)

    def __merge__(self, *args, **kwargs):

        def convert(v):
            d = None
            if isinstance(v, dict):
                d = v
            elif hasattr(v, '__dict__'):
                d = v.__dict__
            return v if d is None else Config(v)

        for arg in args:
            d = None
            if isinstance(arg, dict):
                d = arg
            elif hasattr(arg, '__dict__'):
                d = arg.__dict__
            else: continue
            for (k, v) in d.items():
                self.__setitem__(k, convert(v))

        for (k, v) in kwargs.items():
            self.__setitem__(k, convert(v))




def _represent_ordered_yaml(dumper, data):
    kvs = []
    for item_key, item_value in data.items():
        # find node
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        kvs.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', kvs)



yaml.add_representer(Config,  _represent_ordered_yaml)




