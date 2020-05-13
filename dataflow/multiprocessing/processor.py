


def initializer(envs, init_func, init_args):
    # init global envs
    g = globals()
    for k, v in envs.items(): g[k] = v

    # set

    # call init functions
    if init_func is not None: init_func(*init_args)


def worker(func, envs, *args, **kwargs):

    global __COM_QUEUE__
    try:
        return func(*args, **kwargs)
    except Exception as e:
        import sys
        import traceback
        traceback.print_exc()
        sys.stderr.write(str(e))
        return e
    finally:
        __COM_QUEUE__.put((envs['__TASK_INDEX__'], 'finish'))