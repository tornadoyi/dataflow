import pymysql as ps

def exec(**kwargs):
    host = kwargs.get('host', None)
    port = kwargs.get('port', 3306)
    password = kwargs.get('password', '')
    user = kwargs.get('user', None)
    sql = kwargs.get('sql')
    charset = kwargs.get('charset', 'utf8mb4')
    conn = ps.connect(host=host, port=port, user=user, password=password, charset=charset)
    sqls = sql if isinstance(sql, (tuple, list)) else [sql]
    try:
        cursor = conn.cursor()
        for sql in sqls:
            try:
                cursor.execute(sql)
            except Exception as e:
                error = 'MYSQL execute error:\nSQL:\n{}\nError: {}'.format(
                    sql if len(sql) <= 1024 else sql[:1024] + '...',
                    str(e)
                )
                raise Exception(error)

        conn.commit()
        results = cursor.fetchall()

    finally:
        conn.close()

    return results