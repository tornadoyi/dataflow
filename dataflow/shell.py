import os
import sys
import subprocess
import time
import pickle
import threading
import select



def _read(stream):
    b = stream.read()
    return b'' if b is None else b

def _readlines(stream): return bytes.decode(_read(stream)).rstrip('\n').split('\n')

def _readstr(stream): return bytes.decode(_read(stream))

def _readpickle(stream): return pickle.loads(_read(stream))

def _readsingle(stream): return bytes.decode(_read(stream)).replace('\n', '')


_INTERNAL_OUTPUT_FUNCS = {
    'bytes': _read,
    bytes: _read,
    'str': _readstr,
    str: _readstr,
    'single': _readsingle,
    'lines': _readlines,
    'pickle': _readpickle
}


class Process(object):
    def __init__(self, cmd, timeout=None, retry=0, **kwargs):
        self.__cmd = cmd
        self.__timeout = timeout
        self.__retry = retry
        self.__kwargs = kwargs
        self.__start_time = time.time()

        self.__stdout, self.__stderr = _Buffer(), _Buffer()
        self.__p, self.__t = Process.__create_internal_subprocess(self.__cmd, self.__stdout, self.__stderr, **self.__kwargs)


    @property
    def cmd(self): return self.__cmd

    @property
    def done(self): return self.__p.poll() is not None

    @property
    def pid(self): return self.__p.pid()

    @property
    def returncode(self): return self.__p.returncode

    @property
    def stdin(self): return self.__p.stdin

    @property
    def stdout(self): return self.__stdout

    @property
    def stderr(self): return self.__stderr


    def communicate(self, input=None): return self.__p.communicate(input)

    def send_signal(self, signal): return self.__p.send_signal(signal)

    def terminate(self): return self.__p.terminate()

    def kill(self): return self.__p.kill()

    def wait(self):
        end_time = None if self.__timeout is None else self.__start_time + self.__timeout
        try:
            for i in range(self.__retry+1):
                wait_time = None if self.__timeout is None else max(0, end_time - time.time())
                code = self.__p.wait(wait_time)
                if code == 0: break
                if i < self.__retry:
                    self.__t.join()
                    self.__p, self.__t = Process.__create_internal_subprocess(self.__cmd, self.__stdout, self.__stderr, **self.__kwargs)

        except subprocess.TimeoutExpired:
            pass


    def read_output(self, type=bytes): return _INTERNAL_OUTPUT_FUNCS.get(type, bytes)(self.stdout)


    def read_error(self): return _readstr(self.stderr)



    @staticmethod
    def __create_internal_subprocess(cmd,
                                     stdout,
                                     stderr,
                                     preexec_fn=None,
                                     verbose = 0):


        def _worker(p, stdout, stderr, verbose=0, buffer_size=65535):

            def on_read_stream(b, buf, std, verbose=False):
                if verbose:
                    s = 'unsupoorted message (decode failed)'
                    try:
                        s = b.decode()
                    except: pass
                    std.write(s)
                    std.flush()

                # write to buf
                buf.write(b)


            try:
                fds = [p.stdout, p.stderr]
                while p.poll() is None:
                    rs, ws, es = select.select(fds, fds, fds)
                    for fd in rs + ws + es:
                        if fd == p.stdout:
                            on_read_stream(os.read(fd.fileno(), buffer_size), stdout, sys.stdout, verbose >= 2)
                        elif fd == p.stderr:
                            on_read_stream(os.read(fd.fileno(), buffer_size), stderr, sys.stderr, verbose >= 1)


                bs = p.stdout.read()
                if len(bs) > 0: on_read_stream(bs, stdout, sys.stdout, verbose >= 2)

                bs = p.stderr.read()
                if len(bs) > 0: on_read_stream(bs, stderr, sys.stderr, verbose >= 1)

                return p.returncode == 0

            except Exception as e:
                sys.stderr.write(str(e))


        p = subprocess.Popen(cmd,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             preexec_fn=preexec_fn)


        t = threading.Thread(target=_worker, args=(p, stdout, stderr, verbose))
        t.start()

        return p, t



class _Buffer(object):
    def __init__(self, b=b''):
        self.__data = b
        self.__mutex = threading.Lock()

    def write(self, b):
        self.__mutex.acquire()
        try:
            self.__data += b
        finally:
            self.__mutex.release()

    def read(self):
        self.__mutex.acquire()
        try:
            d = self.__data
            self.__data = b''
            return d
        finally:
            self.__mutex.release()




def run(cmd, **kwargs):
    p = Process(cmd, **kwargs)
    p.wait()
    return p


def run_all(cmds, **kwargs):
    ps = []
    for cmd in cmds: ps.append(Process(cmd, **kwargs))
    for p in ps: p.wait()
    return ps





