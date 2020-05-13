import sys, time
from pyhive import hive
from TCLIService.ttypes import TOperationState
from dataflow import shell


def command_exec(**kwargs):
    sql = kwargs.get('sql')
    timeout = kwargs.get('timeout', None)
    verbose = kwargs.get('verbose', False)
    max_error_length = kwargs.get('max_error_length', 10 * 1024)

    # ensemble sql
    sqls = sql if isinstance(sql, (tuple, list)) else [sql]
    str_sql = ''
    for s in sqls:
        s = s.replace('\n', ' ').replace('\t', ' ').replace('`', '').strip(' ')
        if s[-1] != ';': s += ';'
        str_sql += s

    # run command
    cmd = 'hive -e "{}" '.format(str_sql)
    if not verbose: cmd += '-S'
    p = shell.run(cmd, timeout=timeout, verbose=int(verbose))
    if p.returncode != 0:
        error = 'Hive exec error:\n'
        error += 'SQL: {}\n'.format(str_sql if len(str_sql) <= max_error_length else str_sql[:max_error_length] + '...')
        error += 'Error: {}'.format(p.read_error())
        raise Exception(error)

    # parse results
    lines = p.read_output(type='lines')
    return [ln.split('\t') for ln in lines]






def hive_server_exec(**kwargs):
    connect_kwargs = {
        'host': kwargs.get('host', None),
        'port': kwargs.get('port', None),
        'username': kwargs.get('username', None),
        'database': kwargs.get('database', 'default'),
        'auth': kwargs.get('auth', None),
        'configuration': kwargs.get('configuration', None),
        'kerberos_service_name': kwargs.get('kerberos_service_name', None),
        'password': kwargs.get('password', None),
        'thrift_transport': kwargs.get('thrift_transport', None)
    }

    sql = kwargs.get('sql')
    timeout = kwargs.get('timeout', None)
    verbose = kwargs.get('verbose', False)
    start_time = time.time()

    sqls = sql if isinstance(sql, (tuple, list)) else [sql]

    # create connect
    con = hive.connect(**connect_kwargs)
    try:
        cursor = con.cursor()

        # execute
        for sql in sqls:
            try:
                cursor.execute(sql, async=True)
            except Exception as e:
                sys.stderr.write('sql execute failed, sql: {}\n{}'.format(sql, str(e)))
                raise e

        # wait results
        status = cursor.poll().operationState
        while status in (TOperationState.INITIALIZED_STATE, TOperationState.RUNNING_STATE):
            # print log
            if verbose is True:
                logs = cursor.fetch_logs()
                for message in logs:
                    sys.stdout.write(message)

            # check timeout
            if timeout is not None and time.time() - start_time >= timeout:
                cursor.cancel()
                raise Exception('hive execute timeout({}/{})'.format(time.time() - start_time, timeout))

            # update status
            status = cursor.poll().operationState

        # fetch all datas
        return cursor.fetchall()

    finally:
        con.close()


exec = command_exec