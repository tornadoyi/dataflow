import threading
from easydict import EasyDict as edict
from functools import partial
from .pool import Pool
from dataflow import time


class Task(object):
    def __init__(self, children=None):
        self._children = children or []
        self._parents = []

        # set child
        for c in self._children: c._add_parent(self)


    def __call__(self, *args, **kwargs): raise Exception('__call__ should be implemented')


    @property
    def children(self): return self._children

    @property
    def parents(self): return self._parents

    def _add_parent(self, t): self._parents.append(t)



class TaskManager(object):
    def __init__(self, tasks, tick=1e-3, **kwargs):
        self._pool = Pool(**kwargs)
        self._init_tasks = tasks
        self._tasks = {}
        self._tick = tick
        self._process_thread = None
        self._mutex = threading.Lock()
        self._error = None

        # parse init task
        self._parse_init_task()

    @property
    def tasks(self):
        return len(self._tasks)

    @property
    def finishes(self):
        finish_count = 0
        for _, info in self._tasks.items():
            if info.ar is None or not info.ar.ready: continue
            finish_count += info.ar.finishes
        return finish_count

    @property
    def error(self): return self._error



    def __call__(self, *args, **kwargs):

        finish_task_count = 0
        def _callback(e):
            nonlocal finish_task_count
            finish_task_count += 1

        def _worker():
            running = True

            while running:
                # execute
                self._mutex.acquire()
                try:
                    ready_tasks = self._get_ready_tasks()
                    for t, args in ready_tasks:
                        self._tasks[t].ar = self._pool.apply_async(t, args, callback=_callback, error_callback=_callback)
                    if finish_task_count >= len(self._tasks): break
                except Exception as e:
                    self._error = e
                    raise e
                finally:
                    self._mutex.release()
                time.sleep(self._tick)



        self._process_thread = threading.Thread(target=_worker, name='task_manager', daemon=True)
        self._process_thread.start()


    def wait(self): self._process_thread.join()


    def _get_ready_tasks(self):
        candidates = []
        for t, info in self._tasks.items():
            # check finish
            ar = self._tasks[t].ar
            if ar is not None: continue

            # check children
            finish = True
            for c in t.children:
                ar = self._tasks[c].ar
                if ar and ar.ready: continue
                finish = False
                break
            if not finish: continue

            # get arguments
            args = []
            for c in t.children:
                a = self._tasks[c].ar.get()
                if isinstance(a, Exception): raise a
                args.append(a)
            candidates.append((t, args))

        return candidates


    def _parse_init_task(self):
        def _parse(t):
            if t in self._tasks: raise Exception('Repeated task {}'.format(t))
            self._tasks[t] = edict(ar=None)
            for c in t.children: _parse(c)

        for t in self._init_tasks: _parse(t)



