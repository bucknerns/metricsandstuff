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
            "skipped": self.skipped,
            "failed": self.failed,
            "passed": self.passed,
            "run_at": self.run_at,
            "run_time": self.run_time}
        dic["metadata"] = self.metadata or {}
        return dic

    @classmethod
    def from_redis(cls, data):
        metadata = {
            k.split(":", 1)[-1]: v for k, v in data.items()
            if k.startswith(Run.METADATA.format(""))}
        return cls(
            failed=int(data.get(Run.FAILED)),
            run_id=str(data.get(Run.RUN_ID)),
            metadata=metadata,
            passed=int(data.get(Run.PASSED)),
            run_at=parse_date_string(data.get(Run.RUN_AT)),
            run_time=float(data.get(Run.RUN_TIME)),
            skipped=int(data.get(Run.SKIPPED)))

    @classmethod
    def from_user_dict(cls, data):
        # The user cannot send in calculated values thus failed passed and
        # skipped are not parsed here
        return cls(
            metadata=cls._api.handle_dict(data.get("metadata"), "metadata"),
            run_at=cls._api.handle_date(data.get("run_at"), "run_at", False),
            run_time=cls._api.handle_float(data.get("run_time"), "run_time", False))
