import json
import re
import uuid
from myapp.common.utils import parse_date_string, parse_date_ts
from myapp.elasticsearch.client import ElasticsearchClient as ESC


class Run(object):
    def __init__(self):
        self.run_id = None
        self.run_at = None
        self.run_time = None
        self.metadata = {}

    def generate_run_id(self):
        return str(uuid.uuid4())

    def send(self, client, target='es'):
        if target == 'es':
            self.run_id = self.generate_run_id()
            client.create_run(
                self.run_id, self.run_at, run_time=self.run_time,
                metadata=self.metadata)

        elif target == 'api':
            pass


class TestObj(object):
    def __init(self):
        self.test_id = None
        self.run_id = None
        self.test_name = None
        self.status = None
        self.start_time = None
        self.end_time = None
        self.metadata = {}

    def generate_test_id(self):
        return str(uuid.uuid4())

    def send(self, client, target='es'):
        if target == 'es':
            self.test_id = self.generate_test_id()
            r = client.create_test(
                self.test_id, self.run_id, self.test_name, self.status,
                self.start_time, self.end_time)
            print r.ok, r.status_code, r.content

        elif target == 'api':
            pass


def generate_run_record(hit, client):
    run = Run()
    run.run_at = hit.get('_source').get('@timestamp')
    run.run_time = hit.get('_source').get('data').get('buildDuration')
    return run


def generate_test_records(hit, run, client):
    # Generate Tests
    tests = hit.get('_source').get('message')
    test_regex = (
        r'(?P<test_name>^test_\S+)\s.*(?P<test_class_path>\(.*\))\s\.\.\.\s'
        '(?P<result>.*$)')
    for line in tests:
        m = re.search(test_regex, line)
        if m is None:
            continue
        tstobj = TestObj()
        # test_class_path = m.group('test_class_path')
        tstobj.run_id = run.run_id
        tstobj.test_name = m.group('test_name')
        tstobj.status = (
            'passed' if m.group('result') == 'ok' else
            'failed' if m.group('result') == 'FAIL'else
            'skipped' if m.group('result') == 'skipped' else
            m.group('result'))
        tstobj.start_time = run.run_at
        tstobj.end_time = parse_date_string(
            parse_date_ts(run.run_at)
            + (float(run.run_time) / 1000.0))

data = None
with open('records.json') as data_file:
    data = json.load(data_file)

hits = data.get('hits').get('hits')
client = ESC()
test_count = 0
for hit in hits:
    run = generate_run_record(hit)
    run.send(client)
    tests = generate_test_records(hit, run)
    for test in tests:
        test.send(client)
    test_count += len(test)

print "Done: {} Runs / {} Tests uploaded".format(len(hits), test_count)
