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
            "test_id": str(self.test_id),
            "run_id": str(self.run_id),
            "status": str(self.status),
            "start_time": parse_date_string(self.start_time),
            "stop_time": parse_date_string(self.stop_time),
            "test_name": str(self.test_name)}
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
    def from_dict(cls, data):
        return cls(
            metadata=data.get("metadata", {}),
            run_id=data.get("run_id"),
            start_time=data.get("start_time"),
            status=data.get("status"),
            stop_time=data.get("stop_time"),
            test_id=data.get("test_id"),
            test_name=data.get("test_name"))
