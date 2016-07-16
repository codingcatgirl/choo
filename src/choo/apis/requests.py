import json
import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime
from pprint import pprint

import defusedxml.ElementTree as ET
import requests


class Request(ABC):
    requests_dump = []

    @abstractmethod
    def __init__(self, api):
        self.api = api
        self.time = datetime.now()

    def _url_filter(self, endpoint, method):
        return endpoint

    def _post(self, endpoint, data, session=requests):
        return self._request('POST', endpoint, data, session=session)

    def _get(self, endpoint, session=requests):
        return self._request('GET', endpoint, session=session)

    def _request(self, method, endpoint, data=None, session=requests):
        url = self._url_filter(endpoint)
        if os.environ.get('CHOO_DEBUG'):
            print('=== %s: %s ===' % (method, url))
            if method == 'POST':
                pprint(data)
            print('='*70)

        if os.environ.get('CHOO_REQUESTS_TEST'):
            if os.environ.get('CHOO_REQUESTS_TEST_ORDERED'):
                request = self.requests_dump.pop(0)
            else:
                for i, request in enumerate(self.requests_dump):
                    if request['method'] == method and request['url'] == url:
                        if request['method'] != 'POST' or request['data'] == data:
                            break
                else:
                    raise AssertionError('Request not found in dump: %s %s %s' % (method, url, repr(data)))
                self.requests_dump.pop(i)

            if not os.environ.get('CHOO_REQUESTS_TEST_FORCE_REQUEST'):
                return self._parse_result_to_data(request['result'])

        if method == 'POST':
            result = session.post(url, data)
        elif method == 'GET':
            result = session.get(data)

        if os.environ.get('CHOO_REQUESTS_DUMP'):
            dump = OrderedDict((
                ('method', method),
                ('url', url),
            ))
            if method == 'POST':
                dump['data'] = data
            dump['result'] = result.text
            Request.requests_dump.append(dump)

        return self._parse_result_to_data(result.text)

    def _parse_result(self, result):
        open('dump.xml', 'w').write(result.text)
        return self._parse_result_to_data(result)

    @classmethod
    @abstractmethod
    def _parse_result_to_data(cls, result):
        pass


class XMLRequest(Request):
    @classmethod
    def _parse_result_to_data(self, result):
        return ET.fromstring(result)


class JSONRequest(Request):
    def _parse_result_to_data(self, result):
        return json.loads(result)
