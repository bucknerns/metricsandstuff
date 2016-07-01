import json

from myapp.common.utils import parse_date_string, parse_date_ts
from myapp.common.client import BaseHTTPClient


class ElasticsearchClient(BaseHTTPClient):
    def __init__(self, url="http://localhost:9200", index="metrics"):
        super(ElasticsearchClient, self).__init__(url)
        self.index = index
        self.headers = {"Content-Type": "application/json"}
        self.create_index()

    def create_run(
            self, run_id, run_at, run_time=0, metadata=None):
        metadata = metadata or {}
        entries = []
        url = "{0}/{1}/_bulk".format(self.url, self.index)
        data = {
            "start_time": parse_date_string(run_at),
            "end_time": parse_date_string(
                parse_date_ts(run_at) + parse_date_ts(run_time))}

        # Add metadata to run as keys for now
        for k, v in metadata.items():
            data[k] = v

        self.add_bulk_entry(entries, "run", data, id_=run_id)
        for k, v in metadata.items():
            data = {"key": k, "value": v}
            self.add_bulk_entry(
                entries, "run_metadata", data, None, parent=run_id)
        return self.post(url, data="\n".join(entries) + "\n")

    def create_test(
        self, test_id, run_id, test_name, status, start_time, end_time,
            metadata=None):
        metadata = metadata or {}
        entries = []
        url = "{0}/{1}/_bulk".format(self.url, self.index)
        start_time = parse_date_string(start_time)
        end_time = parse_date_string(end_time)
        data = {
            "test_name": test_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time}

        # Add metadata to test as keys for now
        for k, v in metadata.items():
            data[k] = v

        self.add_bulk_entry(entries, "test", data, id_=test_id, parent=run_id)
        for k, v in metadata.items():
            data = {"key": k, "value": v}
            self.add_bulk_entry(
                entries, "test_metadata", data, None, parent=test_id)
        return self.post(url, data="\n".join(entries) + "\n")

    def create_index(self):
        data = json.dumps({
            "mappings": {
                "run": {},
                "run_metadata": {"_parent": {"type": "run"}},
                "test": {"_parent": {"type": "run"}},
                "test_metadata": {"_parent": {"type": "test"}}}})
        return self.put("{0}/{1}".format(self.url, self.index), data=data)

    def add_bulk_entry(self, entries, type_, data, id_=None, parent=None):
        dic = {}
        dic["_index"] = self.index
        dic["_type"] = type_
        if id_:
            dic["_id"] = id_
        if parent:
            dic["_parent"] = parent
        meta = {"index": dic}
        entries.append(json.dumps(meta))
        entries.append(json.dumps(data))
        return entries
