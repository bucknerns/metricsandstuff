from myapp.common.client import BaseHTTPClient
from myapp.models.test import TestModel
from myapp.models.run import RunModel
from myapp.models.attachment import AttachmentModel


class APIClient(BaseHTTPClient):
    def __init__(self, url="http://127.0.0.1/api", *args, **kwargs):
        super(APIClient, self).__init__(url, *args, **kwargs)
        self.headers["Content-Type"] = "application/json"

    def create_test(
        self, run_id=None, test_name=None, status=None, start_time=None,
            stop_time=None, metadata=None):
        url = "{0}/tests".format(self.url)
        model = TestModel(
            run_id=run_id,
            status=status,
            start_time=start_time,
            stop_time=stop_time,
            metadata=metadata,
            test_name=test_name)
        r = self.post(url, data=model.to_server())
        r.entity = TestModel.from_server(r.content)
        return r

    def create_run(self, run_time=None, run_at=None, metadata=None):
        url = "{0}/runs".format(self.url)
        model = RunModel(
            run_at=run_at,
            run_time=run_time,
            metadata=metadata)
        r = self.post(url, data=model.to_server())
        r.entity = RunModel.from_server(r.content)
        return r

    def create_attachment(
            self, name=None, data=None, test_id=None, run_id=None):
        url = "{0}/attachments".format(self.url)
        model = AttachmentModel(
            name=name,
            data=data,
            test_id=test_id,
            run_id=run_id)
        r = self.post(url, data=model.to_server())
        r.entity = AttachmentModel.from_server(r.content)
        return r
