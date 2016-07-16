#!/usr/bin/env python3
import json
import os
from datetime import datetime

from choo.apis import *  # noqa
from choo.apis.requests import Request

print('Please enter Query command:')
command = input('Enter Query command: ')

print('')
ordered_requests = ''
while ordered_requests not in ['Y', 'N']:
    ordered_requests = input('Requests are ordered? [Y/n] ').strip().upper()
    if ordered_requests == '':
        ordered_requests = 'Y'
ordered_requests = (ordered_requests == 'Y')

os.environ['CHOO_REQUESTS_DUMP'] = '1'
query = eval(command)
query.execute()

print('import os\n')
print('from choo.apis import *  # noqa')
print('from choo.apis.requests import Request\n\n')

print('class Test'+query.api.name.title()+query.__class__.__name__+':')
print('    def test_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'(self):')
requests_dump = json.dumps(Request.requests_dump, ensure_ascii=False, indent=4).replace('\n', '\n        ')
requests_dump = '\n'.join((line if len(line) < 120 else (line+'  # noqa')) for line in requests_dump.split('\n'))
print('        Request.requests_dump = '+requests_dump)
print('        os.environ["CHOO_REQUESTS_TEST"] = "1"')
if ordered_requests:
    print('        os.environ["CHOO_REQUESTS_TEST_ORDERED"] = "1"')
query_result = json.dumps(query.serialize(), ensure_ascii=False, indent=4).replace('\n', '\n        ')
query_result = query_result.replace('null,\n', 'None,\n').replace('null\n', 'None\n')
print('        query = '+command)
print('        assert query.execute().serialize() == '+query_result)
print('        os.environ.pop("CHOO_REQUESTS_TEST")')
if ordered_requests:
    print('        os.environ.pop("CHOO_REQUESTS_TEST_ORDERED")')
