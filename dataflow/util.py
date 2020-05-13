import signal
import os

exit_callbacks = []

def register_exit_signal_callback(f):
    def handle_signals(signum, frame):
        for f in exit_callbacks:
            try:
                f()
            except: pass
        exit(0)

    if len(exit_callbacks) == 0:
        signal.signal(signal.SIGINT, handle_signals)
        signal.signal(signal.SIGTERM, handle_signals)

    exit_callbacks.insert(0, f)



def start_aync_loop(f):
    import asyncio
    loop = asyncio.get_event_loop()

    def handler_exit():
        loop.close()
    register_exit_signal_callback(handler_exit)

    loop.run_until_complete(f)
    loop.close()



def __multiprocessing_async_func(func, args):
    try:
        return func(*args)
    except Exception as e:
        return e


def start_multiprocessing(processors, **kwargs):
    import multiprocessing

    def __handle_error(e): raise e

    callback = kwargs.get('callback', None)
    error_callback = kwargs.get('error_callback', __handle_error)

    pool = multiprocessing.Pool(processes=len(processors))
    async_results = []
    for i in range(len(processors)):
        func, args = processors[i]
        async_results.append(pool.apply_async(func, args, callback=callback, error_callback=error_callback))
    pool.close()

    results = []
    for ar in async_results:
        r = ar.get()
        results.append(r)

    return results

