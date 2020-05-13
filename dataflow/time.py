import sys
from time import *


__TIME_UNITS = ['y', 'm', 'd', 'H', 'M', 'S']


# https://docs.python.org/3/library/time.html#time.gmtime
__TIME_UNIT_RANGE = (
    (0, sys.maxsize),   # year
    (1, 12),            # month
    (1, 31),            # day
    (0, 23),            # hour
    (0, 59),            # minute
    (0, 61),            # second
    (0, 6),             # weekday
    (1, 366),           # day in years
    (0, 1)              # tm_isdst
)

__TIME_UNIT_RANGE_LOW = tuple([r[0] for r in __TIME_UNIT_RANGE])

__TIME_UNIT_RANGE_HIGH = tuple([r[1] for r in __TIME_UNIT_RANGE])



start_time = mktime(localtime())

def curtime(): return mktime(localtime())


def format(fmt, t):
    st = localtime(t)
    return strftime(fmt, st)

encode = format

def decode(fmt, strtime):
    tm = strptime(strtime, fmt)
    return mktime(tm)

def trim_year(t): return trim_time(t, 0)

def trim_month(t): return trim_time(t, 1)

def trim_day(t): return trim_time(t, 2)

def trim_hour(t): return trim_time(t, 3)

def trim_minute(t): return trim_time(t, 4)

def trim_second(t): return trim_time(t, 5)


def trim_time(t, index):
    st = localtime(t)
    list_time = list(st[:index+1]) + list(__TIME_UNIT_RANGE_LOW[index+1:])
    return mktime(tuple(list_time))





