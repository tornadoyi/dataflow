import os
import stat
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, BaseRotatingHandler
from dataflow.config import CFG_LOG
from dataflow import time

class ScheduleRotatingHandler(BaseRotatingHandler):
    def __init__(self, filename, when='h', backupCount=0, **kwargs):
        super(ScheduleRotatingHandler, self).__init__(filename, 'a', **kwargs)

        self.when = when
        self.backupCount = backupCount

        if self.when == 'S':
            self.log_time = time.curtime()
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.interval = 1  # one second
        elif self.when == 'M':
            self.log_time = time.trim_minute(time.curtime())
            self.suffix = "%Y-%m-%d_%H-%M"
            self.interval = 60  # one minute
        elif self.when == 'H':
            self.log_time = time.trim_hour(time.curtime())
            self.suffix = "%Y-%m-%d_%H"
            self.interval = 60 * 60  # one hour
        elif self.when == 'D':
            self.log_time = time.trim_day(time.curtime())
            self.suffix = "%Y-%m-%d"
            self.interval = 60 * 60 * 24  # one day
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

        self.rolloverAt = self.log_time + self.interval

        # check rollover
        t = self._trim_time(os.stat(self.baseFilename)[stat.ST_MTIME])
        if self.log_time != t: self.doRollover()


    def doRollover(self):
        # change stream
        if self.stream:
            self.stream.close()
            self.stream = None

        # rename
        if os.path.isfile(self.baseFilename):
            t = self._trim_time(os.stat(self.baseFilename)[stat.ST_MTIME])
            dst_file_name = self.baseFilename + '.' + time.strftime(self.suffix, time.localtime(t))
            if not os.path.isfile(dst_file_name):
                os.rename(self.baseFilename, dst_file_name)

        if not self.delay:
            self.stream = self._open()


        # clean old files
        self.clean_old_files()



    def shouldRollover(self, record=None): return time.curtime() >= self.rolloverAt


    def clean_old_files(self):
        _fmt = ['%Y', '%Y-%m', '%Y-%m-%d', '%Y-%m-%d-%H', '%Y-%m-%d-%H-%M', '%Y-%m-%d-%H-%M-%S']
        dir_path = os.path.dirname(self.baseFilename)
        base_file_name = os.path.basename(self.baseFilename)
        del_files = []
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if not os.path.isfile(file_path): continue
            if not file.startswith(base_file_name): continue
            try:
                time_ext = file.split('.')[-1].replace('_', '-')
                s = time_ext.split('-')
                f = _fmt[len(s)-1]
                t = time.mktime(time.strptime(time_ext, f))
                if t >= self.log_time: continue
                del_files.append((t, os.path.join(dir_path, file)))

            except: continue

        sorted_files = sorted(del_files, key=lambda x: x[0])
        delcount =  max(len(sorted_files) - self.backupCount, 0)
        for i in range(delcount):
            os.remove(sorted_files[i][1])


    def _trim_time(self, t):
        if self.when == 'S': return t
        elif self.when == 'M': return time.trim_minute(t)
        elif self.when == 'H': return time.trim_hour(t)
        elif self.when == 'D': return time.trim_day(t)
        else: raise ValueError("Invalid rollover interval specified: %s" % self.when)





_HANDLERS = {
    'RotatingFileHandler': RotatingFileHandler,
    'TimedRotatingFileHandler': TimedRotatingFileHandler,
    'ScheduleRotatingHandler': ScheduleRotatingHandler,
}


# define my logger
class Logger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)
        self.__init = False


    @property
    def init(self): return self.__init

    def initialize(self, file, formatter=None, level=CFG_LOG.LEVEL, handlers=[CFG_LOG.DEFAULT_HANDLER]):
        # check init tag
        if self.__init: return

        # create log dir
        file_dir = os.path.dirname(file)
        os.makedirs(file_dir, exist_ok=True)

        # set formatter
        if formatter is None: formatter = logging.Formatter(CFG_LOG.LOG_FORMAT, CFG_LOG.DATE_FORMAT)

        # set level
        self.setLevel(level)

        # create file handler
        for cfg in handlers:
            name, kwargs = None, {}
            for k, v in cfg.items():
                if k == 'name': name = v
                else: kwargs[k] = v
            fh = _HANDLERS[name](file, **kwargs)
            fh.setFormatter(formatter)
            self.addHandler(fh)

        # create stream handler
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        self.addHandler(sh)


        # set tag
        self.__init = True



# reset default logger
logging.setLoggerClass(Logger)


def get_logger(file, *args, **kwargs):

    # create logger
    logger = logging.getLogger(file)

    # initialize
    logger.initialize(file, *args, **kwargs)

    return logger








