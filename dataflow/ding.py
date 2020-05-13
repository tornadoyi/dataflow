import json
from dataflow import http

__URL_GET_TOKEN = 'http://dd.app.corpautohome.com/api/ding/gettoken?appid={}&appkey={}'

__URL_SEND = 'http://dd.app.corpautohome.com/api/ding/send?access_token={}'


def send(app_id, app_key, body):
    # get token
    r = http.get(url=__URL_GET_TOKEN.format(app_id, app_key))
    if r.status != 200: raise Exception('Get token response error, error code: {}'.format(r.status))
    d = json.loads(r.data)
    token = d['access_token']

    # send
    if isinstance(body, dict): body = json.dumps(body, ensure_ascii=False)
    body = body.encode('utf-8')
    r = http.post(__URL_SEND.format(token), body=body)
    if r.status != 200: raise Exception('Send message response error, error code: {}'.format(r.status))