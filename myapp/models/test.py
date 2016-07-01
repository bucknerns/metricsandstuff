from myapp.models.base import BaseModel
from myapp.redis.db_layout import Test
from myapp.common.utils import parse_date_string


class TestModel(BaseModel):
    def __init__(
        self, test_id=None, run_id=None, status=None, start_time=None,
            stop_time=None, metadata=None, test_name=None):
        super(TestModel, self).__init__(locals())

    def to_dict(self):
        dic = {
            "test_id": self.test_id,
            "run_id": self.run_id,
            "status": self.status,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "test_name": self.test_name}
        dic["metadata"] = self.metadata or {}
        return dic

    @classmethod
    def from_redis(cls, data):
        metadata = {
            k.split(":", 1)[-1]: v for k, v in data.items()
            if k.startswith(Test.METADATA.format(""))}
        start = parse_date_string(data.get(Test.START_TIME))
        stop = parse_date_string(
            float(data.get(Test.START_TIME)) + float(data.get(Test.RUN_TIME)))
        return cls(
            metadata=metadata,
            run_id=data.get(Test.RUN_ID),
            start_time=start,
            status=data.get(Test.STATUS),
            stop_time=stop,
            test_id=data.get(Test.ID),
            test_name=data.get(Test.NAME))

    @classmethod
    def from_user_dict(cls, data):
        return cls(
            metadata=cls._api.handle_dict(data.get("metadata"), "metadata"),
            run_id=data.get("run_id"),
            start_time=cls._api.handle_date(
                data.get("start_time"), "start_time"),
            status=cls._api.handle_test_status(data.get("status")),
            stop_time=cls._api.handle_date(data.get("stop_time"), "stop_time"),
            test_name=cls._api.handle_string(
                data.get("test_name"), "test_name"))

    @classmethod
    def from_server_dict(cls, data):
        return cls(
            test_id=data.get("test_id"),
            run_id=data.get("run_id"),
            status=data.get("status"),
            start_time=data.get("start_time"),
            stop_time=data.get("stop_time"),
            metadata=data.get("metadata"),
            test_name=data.get("test_name"))

    def to_server_dict(self):
        dic = {
            "run_id": self.run_id,
            "status": self.status,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "test_name": self.test_name}
        dic["metadata"] = self.metadata or {}
        return dic
