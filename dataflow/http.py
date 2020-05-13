import http.client
from easydict import EasyDict as edict

def request(method, url, body=None, headers={}, **kwargs):
    # parse protocal, host, port and uri
    s = url.split('://')
    if len(s) != 2: raise Exception('can not parse protocal from url {}'.format(url))
    protocal, host_uri = s[0].upper(), s[1]
    s = host_uri.split('/', 1)
    host_port = s[0]
    uri = '' if len(s) <= 1 else s[1]
    s = host_port.split(':')
    host = s[0]
    port = None if len(s) <= 1 else int(s[1])

    # create connection
    if protocal == 'HTTP':
        conn_class = http.client.HTTPConnection
        conn_kwargs = {'timeout': kwargs.get('timeout', None),
                       'source_address': kwargs.get('source_address', None)}
    elif protocal == 'HTTPS':
        conn_class = http.client.HTTPSConnection
        conn_kwargs = {'key_file': kwargs.get('key_file', None),
                       'cert_file': kwargs.get('cert_file', None),
                       'timeout': kwargs.get('timeout', None),
                       'source_address': kwargs.get('source_address', None),
                       'context': kwargs.get('context', None),
                       'check_hostname': kwargs.get('check_hostname', None)}
    else: raise Exception('invalid protocal {}'.format(protocal))
    conn = conn_class(host, port, **conn_kwargs)

    # request
    try:
        request_kwargs = {'encode_chunked': kwargs.get('encode_chunked', False)}
        conn.request(method, '/{}'.format(uri), body, headers, **request_kwargs)
        r = conn.getresponse()
        return edict(
            data = r.read(),
            headers = r.getheaders(),
            version = r.version,
            status = r.status,
            reason = r.reason,
            debuglevel = r.debuglevel
        )
    finally:
        conn.close()



def get(url, *args, **kwargs): return request('GET', url, *args, **kwargs)


def post(url, *args, **kwargs): return request('POST', url, *args, **kwargs)