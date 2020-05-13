from __future__ import absolute_import, division, print_function

import os
import tempfile

try:
    import portalocker
except:
    class FakeLocker(object):
        LOCK_EX = 0
        LOCK_NB = 0
        def lock(self, fd, type): pass
        def unlock(self, fd): pass
    portalocker = FakeLocker()



def singleton(cls):
    def wrapper(*args, **kwargs):
        if not hasattr(cls, '__instance'):
            cls.__instance = cls(*args, **kwargs)
        return cls.__instance

    return wrapper


@singleton
class SingletonApplication(object):
    def __init__(self, name=None, pid_file_path=None):
        # lock file path
        if pid_file_path:
            self.__pid_file_path = pid_file_path
        else:
            if name is None: raise Exception('Need application name')
            self.__pid_file_path = os.path.join(tempfile.gettempdir(), '{}.pid'.format(name))

        # exist
        self.__initialized = True
        self.__fd = open(self.__pid_file_path, 'w')

        try:
            #fcntl.lockf(self.__fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            portalocker.lock(self.__fd, portalocker.LOCK_EX | portalocker.LOCK_NB)
        except IOError:
            self.__initialized = False

        # pid
        if self.__initialized:
            self.__pid = os.getpid()
            self.__fd.write('{}'.format(self.__pid))
            self.__fd.flush()
        else:
            with open(self.__pid_file_path, 'r') as f:
                self.__pid = int(f.read())

    def __del__(self):
        if self.__fd is not None:
            #fcntl.lockf(self.__fd, fcntl.LOCK_UN)
            portalocker.unlock(self.__fd)
            self.__fd.close()   # windows must close fd before remove file

        if os.path.isfile(self.__pid_file_path):
            os.remove(self.__pid_file_path)


    @property
    def initialized(self):
        return self.__initialized

    @property
    def pid(self):
        return self.__pid

    @property
    def pid_file_path(self):
        return self.__pid_file_path



def start(name):
    app = SingletonApplication(name)
    if not app.initialized: raise Exception('A instance process {} has been lanuched'.format(app.pid))
    return app