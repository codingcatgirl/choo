import os
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pprint

import defusedxml.ElementTree as ET


class Request(ABC):
    @abstractmethod
    def __init__(self, api):
        self.api = api
        self.time = datetime.now()

    def _parse_result(self, result):
        if os.environ.get('CHOO_DEBUG'):
            pprint(result.request.__dict__)
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
