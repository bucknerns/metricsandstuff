import json

from myapp.common.client import BaseRaxClient


class APIClient(BaseRaxClient):
    def create_test(
        self, run_id=None, test_name=None, status=None, start_time=None,
            end_time=None, metadata=None):
        url = "{0}/tests".format(self.url)
        return self.s.post(url, data=json.dumps({
            "run_id": run_id,
            "test_name": test_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "metadata": metadata}))

    def create_run(self, run_time=None, run_at=None, metadata=None):
        url = "{0}/runs".format(self.url)
        return self.s.post(url, data=json.dumps({
            "run_time": run_time,
            "run_at": run_at,
            "metadata": metadata}))
