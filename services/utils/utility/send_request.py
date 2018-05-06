# -*- coding:utf-8 -*-
import urllib3
import json
import logging


http = urllib3.PoolManager()


def request(method, url, fields=None, headers=None, **urlopen_kw):
    '''send request to url

    >>> data = request('GET', 'http://120.26.2.230:5010/ml/d1_features/AFF91726-DC26-E511-87D5-80DB2F14945F')   # 5DBF2EDE-F5C4-436F-81C5-10D768797D96
    >>> data['data']['d1_idcard_hometown']
    510183
    >>> data = request('GET', 'http://www.baidu.com')
    >>> print(data)
    {'status': 0, 'data': {}}
    '''
    status = 0    # 1: Success, 0: Failed
    data = {}
    try:
        urlopen_kw.setdefault('timeout', 10)
        response = http.request(method, url, fields, headers, **urlopen_kw)
        loginfo = 'request status:{status}, url:{url}, method:{method}'.format(status=response.status, url=url, method=method)
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))  # loads->unicode
            status = 1
            logging.info(loginfo)
        else:
            logging.error(loginfo)
    except (TypeError, ValueError) as e:
        # logging.error(repr(e))
        logging.error('the response of the request:{url} is not json format'.format(url=url))
    except Exception as e:
        logging.error(repr(e))

    return {'status': status, 'data': data}
