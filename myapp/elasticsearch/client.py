import requests
import json

from myapp.common.utils import parse_date_string


class ElasticsearchClient(object):
    def __init__(self, url="http://localhost:9200", index="metrics"):
        self.index = index
        self.url = url
        self.s = requests.Session()
        self.s.verify = False
        self.s.headers = {"Content-Type": "application/json"}

    def create_run(self, run_id, run_at, run_time=0, metadata=None):
        metadata = metadata or {}
        url = "{0}/{1}/run/{2}".format(self.url, self.index, run_id)
        metadata = {"meta:{0}".format(k): v for k, v in metadata.items()}
        mapping = {
            "run_at": parse_date_string(run_at),
            "run_time": run_time}
        mapping.update(metadata)
        return self.s.post(url, data=json.dumps(mapping))

    def create_test(
        self, test_id, run_id, test_name, status, start_time, end_time,
            metadata=None):
        metadata = metadata or {}
        url = "{0}/{1}/test/{2}".format(self.url, self.index, test_id)
        metadata = {"meta:{0}".format(k): v for k, v in metadata.items()}
        params = {"parent": str(run_id)}
        start_time = parse_date_string(start_time)
        end_time = parse_date_string(end_time)
        mapping = {
            "test_name": test_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time}
        mapping.update(metadata)
        return self.s.post(url, data=json.dumps(mapping), params=params)

    def init_test_mapping(self):
        data = json.dumps({"test": {"_parent": {"type": "run"}}})
        return self.s.put(
            "{0}/{1}/test/_mapping".format(self.url, self.index), data=data)

    def init_run_mapping(self):
        data = json.dumps({"run": {}})
        return self.s.put(
            "{0}/{1}/run/_mapping".format(self.url, self.index), data=data)

    def init_run_metadata_mapping(self):
        data = json.dumps({"run_metadata": {"_parent": {"type": "run"}}})
        return self.s.put(
            "{0}/{1}/run_metadata/_mapping".format(self.url, self.index),
            data=data)
