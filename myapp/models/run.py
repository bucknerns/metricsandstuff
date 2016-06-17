from myapp.models.base import BaseModel
from myapp.redis.db_layout import Run
from myapp.common.utils import parse_date_string


class RunModel(BaseModel):
    def __init__(
        self, run_id=None, skipped=None, failed=None, passed=None, run_at=None,
            run_time=None, metadata=None):
        super(RunModel, self).__init__(locals())

    def to_dict(self):
        dic = {
            "run_id": self.run_id,
            "skipped": int(self.skipped),
            "failed": int(self.failed),
            "passed": int(self.passed),
            "run_at": parse_date_string(self.run_at),
            "run_time": float(self.run_time)}
        dic["metadata"] = self.metadata or {}
        return dic

    @classmethod
    def from_redis(cls, data):
        metadata = {
            k.split(":", 1)[-1]: v for k, v in data.items()
            if k.startswith(Run.METADATA.format(""))}
        return cls(
            failed=data.get(Run.FAILED),
            run_id=data.get(Run.RUN_ID),
            metadata=metadata,
            passed=data.get(Run.PASSED),
            run_at=parse_date_string(data.get(Run.RUN_AT)),
            run_time=data.get(Run.RUN_TIME),
            skipped=data.get(Run.SKIPPED))

    @classmethod
    def from_dict(cls, data):
        return cls(
            failed=data.get("failed"),
            run_id=data.get("run_id"),
            metadata=data.get("metadata"),
            passed=data.get("passed"),
            run_at=data.get("run_at"),
            run_time=data.get("run_time"),
            skipped=data.get("skipped"))
