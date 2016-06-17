from myapp.models.base import BaseModel
from myapp.redis.db_layout import TestStats


class TestStatsModel(BaseModel):
    def __init__(
        self, test_name, run_count=None, passed=None, failed=None,
            skipped=None):
        super(TestStatsModel, self).__init__(locals())

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "run_count": self.run_count,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped}

    @classmethod
    def from_redis(cls, data):
        return cls(
            test_name=data.get(TestStats.TEST_NAME),
            run_count=data.get(TestStats.RUN_COUNT),
            passed=data.get(TestStats.PASSED),
            failed=data.get(TestStats.FAILED),
            skipped=data.get(TestStats.SKIPPED))
