import json
import re
import uuid
import logging
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
    def __init__(self):
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
            client.create_test(
                self.test_id, self.run_id, self.test_name, self.status,
                self.start_time, self.end_time, metadata=self.metadata)

        elif target == 'api':
            pass


def generate_run_record(hit):
    run = Run()
    run.run_at = hit.get('_source').get('@timestamp')
    source_data = hit.get('_source').get('data')
    run.run_time = source_data.get('buildDuration')
    run.metadata['projectName'] = source_data.get('projectName')

    # FYI: The external loop has to send this run to generate an ID before the
    # generate_test_records can use it.
    return run


def generate_test_records(hit, run):
    # Generate Tests
    tests = hit.get('_source').get('message')
    test_regex = (
        r'(?P<test_name>^test_\S+)\s*\((?P<test_class_path>.*)\)\s\.\.\.\s'
        '(?P<result>.*$)')
    brew_file_module_name_regex = (
        r'^\smodule name:\s.*(?P<brew_test_module_name>.*)$')

    for line in tests:
        tstobj = TestObj()

        m = re.search(brew_file_module_name_regex, line)
        if m:
            tstobj.metadata['module_name'] = m.group('brew_test_module_name')

        m = None
        m = re.search(test_regex, line)
        if m is None:
            continue
        tstobj.metadata['test_class_path'] = m.group('test_class_path')
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
        yield tstobj


data = None
with open('records.json') as data_file:
    data = json.load(data_file)

if __name__ == '__main__':
    root = logging.getLogger()
    root.addHandler(logging.StreamHandler())
    root.setLevel(0)
    hits = data.get('hits').get('hits')
    client = ESC()
    test_count = 0
    for hit in hits:
        run = generate_run_record(hit)
        run.send(client)
        for test in generate_test_records(hit, run):  # tests:
            test.send(client)
            test_count += 1

    print "Done: {} Runs / {} Tests uploaded".format(len(hits), test_count)
