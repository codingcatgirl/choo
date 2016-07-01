import os
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pprint

import defusedxml.ElementTree as ET
import requests


class Request(ABC):
    @abstractmethod
    def __init__(self, api):
        self.api = api
        self.time = datetime.now()

    def _url_filter(self, endpoint, method):
        return endpoint

    def _post(self, endpoint, data, session=requests):
        url = self._url_filter(endpoint)
        if os.environ.get('CHOO_DEBUG'):
            print('=== POST: %s ===' % url)
            pprint(data)
            print('='*70)
        result = requests.post(url, data)
        return self._parse_result_to_data(result)

    def _get(self, endpoint, session=requests):
        url = self._url_filter(endpoint)
        if os.environ.get('CHOO_DEBUG'):
            print('=== GET: %s ===' % url)
        result = requests.get(url)
        return self._parse_result_to_data(result)

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
        return ET.fromstring(result.text)


class JSONRequest(Request):
    def _parse_result_to_data(self, result):
        return result.json()
