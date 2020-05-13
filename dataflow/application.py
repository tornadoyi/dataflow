from __future__ import absolute_import, division, print_function

import sys
import os
import argparse
import traceback
from inspect import isfunction
from functools import partial
from easydict import EasyDict as edict
from dataflow import util



logger = None

cache = None

config = None

path = edict()

_APP_ARGS = None

def initialize(**kwargs):
    global _APP_ARGS, logger, cache, config, path

    if _APP_ARGS is not None: return

    _APP_ARGS = kwargs

    # set path
    log_path = _APP_ARGS.get('log_path', '~/.dataflow/logs')
    cache_path = _APP_ARGS.get('cache_path', '~/.dataflow/caches')
    config_path = _APP_ARGS.get('config_path', '~/.dataflow/configs')
    log_file_name = _APP_ARGS.get('log_file_name', 'dataflow.log')


    logger = _AppLogger(os.path.expanduser(log_path), log_file_name)
    cache = _AppCache(os.path.expanduser(cache_path))
    config = _AppConfig(os.path.expanduser(config_path))

    # add DIY path modules
    for n, p in _APP_ARGS.get('path_modules', {}).items():
        path[n] = _AppPath(os.path.expanduser(p))



def run():
    name = _APP_ARGS.get('name', None)
    description = _APP_ARGS.get('description', '')
    modules = _APP_ARGS.get('modules', None)
    module_add_parser_fname = _APP_ARGS.get('module_add_parser_fname', 'add_parser')
    module_execute_fname = _APP_ARGS.get('module_execute_fname', 'execute')
    root_parser_title = _APP_ARGS.get('root_parser_title', 'Available subcommands')

    # search modules
    module_dict = dict([(n, getattr(modules, n)) for n in dir(modules)
                        if hasattr(getattr(modules, n), module_add_parser_fname) and \
                            hasattr(getattr(modules, n), module_execute_fname)])

    # main parser
    parser = argparse.ArgumentParser(prog=name, description=description)
    sparser = parser.add_subparsers(title=root_parser_title, dest="module")

    # add module parsers
    for _, m in module_dict.items():
        getattr(m, module_add_parser_fname)(sparser)

    # parse args
    args = parser.parse_args()

    # catch exit signals
    util.register_exit_signal_callback(lambda: exit(0))

    # exit by error
    def error_exit(error=None, help=False, mod=None):
        if help:
            parser.print_help()
            print('')

        elif error is not None:
            if mod is not None:
                logger.exception(sys.exc_info())
            else:
                msg = traceback.format_exc()
                sys.stderr.write(msg)

        # exit
        exit(1)

    # check module
    mod = module_dict.get(args.module, None)
    if mod is None: error_exit(help=True)

    # run module
    try:
        # run module
        ok = getattr(mod, module_execute_fname)(args)
        if ok is False: error_exit(help=True)

    except Exception as e:
        error_exit(e, False, mod)






class _AppBase(object):
    def __init__(self, core):
        self._core = core

        # import all functions
        for k in dir(self._core):
            # check function
            v = getattr(self._core, k)
            if not isfunction(v): continue

            # check exist in local class
            if hasattr(self, k): continue

            # set wrapper
            setattr(self, k, self._wrapper(v))


    def _wrapper(self, f): raise NotImplementedError('need to implement _wrapper')



class _AppPath(_AppBase):
    def __init__(self, root_path):
        self._root_path = root_path

        from dataflow import path
        super(_AppPath, self).__init__(path)

    @property
    def dir(self): return self._root_path

    def _wrapper(self, f):
        def call(f, file, *args, **kwargs):
            return f(os.path.join(self._root_path, file), *args, **kwargs)

        return partial(call, f)



class _AppCache(_AppPath):
    pass




class _AppLogger(_AppBase):
    def __init__(self, root_path, file, *args, **kwargs):
        from dataflow import logging
        self._root_path = root_path
        self._logger = logging.get_logger(os.path.join(self._root_path, file), *args, **kwargs)


        super(_AppLogger, self).__init__(logging.Logger)



    def get_logger(self, file, *args, **kwargs):  return _AppLogger(file, *args, **kwargs)

    def _wrapper(self, f):
        def call(f, *args, **kwargs):
            return f(self._logger, *args, **kwargs)

        return partial(call, f)



class _AppConfig(_AppBase):
    def __init__(self, root_path):
        self._root_path = root_path

        from dataflow import config
        super(_AppConfig, self).__init__(config)


    def _wrapper(self, f):
        def call(f, file, *args, **kwargs):
            module_file = os.path.join(self._root_path, file)
            return f(module_file, *args, **kwargs)

        return partial(call, f)
