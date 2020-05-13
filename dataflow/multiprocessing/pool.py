from functools import partial
import threading
import queue
from multiprocessing.pool import Pool as _Pool, ThreadPool as _ThreadPool
from multiprocessing import Queue
from . import processor



class Pool(object):
    def __init__(self, pool='process', initializer=None, initargs=None, **kwargs):
        # this queue receive states of processes
        self._com_queue = Queue()
        self._async_results = []
        self._monitor_thread = None
        self._end = False

        # computing concurrently
        envs = {'__COM_QUEUE__': self._com_queue}

        # create process pool
        if pool == 'process': self._cpool = _Pool
        elif pool == 'thread': self._cpool = _ThreadPool
        else: raise Exception('Invalid multiprocess pool type {}'.format(pool))
        self._pool = self._cpool(
            initializer=processor.initializer,
            initargs=(envs, initializer, initargs),
            **kwargs)

    def __del__(self):
        self.__clean()

    def close(self): self._pool.close()

    def join(self): self._pool.join()

    def terminate(self):
        self._pool.terminate()
        self.__clean()

    def __clean(self):
        if self._end: return
        self._end = True
        if self._monitor_thread is not None:
            self._com_queue.close()
            self._monitor_thread.join()
            self._monitor_thread = None



    def apply(self, func, *args, **kwargs): return self.__do('apply', func, *args, **kwargs)

    def apply_async(self, func, *args, **kwargs): return self.__do_async('apply_async', func, *args, **kwargs)

    def map(self, func, *args, **kwargs): return self.__do('map', func, *args, **kwargs)

    def map_async(self, func, *args, **kwargs): return self.__do_async('map_async', func, *args, **kwargs)

    def imap(self, func, *args, **kwargs): return self.__do('imap', func, *args, **kwargs)

    def imap_unordered(self, func, *args, **kwargs): return self.__do('imap_unordered', func, *args, **kwargs)

    def starmap(self, func, *args, **kwargs): return self.__do('starmap', func, *args, **kwargs)

    def starmap_async(self, func, *args, **kwargs): return self.__do_async('starmap_async', func, *args, **kwargs)

    def __do(self, fname, func, *args, **kwargs): pass

    def __do_async(self, fname, func, *args, **kwargs):
        # create result
        result = AsyncResult(self)

        # create task
        self._async_results.append(result)

        # run
        envs = {'__TASK_INDEX__': len(self._async_results)-1}
        f = getattr(self._pool, fname)
        result._ar = f(partial(processor.worker, func, envs), *args, **kwargs)

        # start monitor
        self.__start_task_monitor()

        return result

    def __start_task_monitor(self):
        if self._monitor_thread is not None: return

        def process_data(data):
            index, type = data[0], data[1]
            r = self._async_results[index]
            if type == 'finish': r._finishes += 1

        def monitor_worker():
            while not self._end:
                try:
                    data = self._com_queue.get(timeout=1.0)
                    process_data(data)
                except queue.Empty: continue
                except: continue

        self._monitor_thread = threading.Thread(target=monitor_worker, name='monitor', daemon=True)
        self._monitor_thread.start()


class AsyncResult(object):
    def __init__(self, pool):
        self._pool = pool
        self._ar = None
        self._finishes = 0
        self._errors = 0


    @property
    def finishes(self): return self._finishes

    @property
    def errors(self): return self._errors

    def get(self, *args, **kwargs): return self._ar.get(*args, **kwargs)

    def wait(self, *args, **kwargs): return self._ar.wait(*args, **kwargs)

    def ready(self, *args, **kwargs): return self._ar.ready(*args, **kwargs)

    def successful(self, *args, **kwargs): return self._ar.successful(*args, **kwargs)