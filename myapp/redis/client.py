import re
from uuid import uuid4
import redis

from myapp.models.test import TestModel
from myapp.models.run import RunModel
from myapp.models.base import ListModel
from myapp.models.stats import TestStatsModel
from myapp.models.attachment import AttachmentModel
from myapp.models.filters import FilterModel, FiltersModel
from myapp.redis.db_layout import Keys, TestStats, Run, Test, Attachment
from myapp.common.utils import parse_date_ts
from myapp.common.constants import (
    TEST_STATUSES, DEFAULT_LIMIT, DEFAULT_PAGE, EXPIRE_SECONDS)


class RedisClient(object):
    def __init__(self, max_age=None, *args, **kwargs):
        self.r = redis.Redis(*args, **kwargs)
        self.max_age = max_age or EXPIRE_SECONDS

    def get_runs(
        self, run_after=None, run_before=None, limit=DEFAULT_LIMIT,
            page=DEFAULT_PAGE, status=None, **metadata):
        tmp = uuid4().get_hex()
        intersect_sets = [
            Keys.RUN_META.format(k, v) for k, v in metadata.items()]
        intersect_sets.append(Keys.RUNS)

        run_after = parse_date_ts(run_after) if run_after else "-inf"
        run_before = parse_date_ts(run_before) if run_before else "+inf"

        if status == "failed":
            intersect_sets.append(Keys.FAILED_RUNS)
        elif status == "passed":
            intersect_sets.append(Keys.PASSED_RUNS)

        if len(intersect_sets) > 1:
            pipe = self.r.pipeline()
            pipe.zinterstore(tmp, intersect_sets, aggregate="max")
            pipe.zrevrangebyscore(
                tmp, run_before, run_after, limit * (page - 1), limit)
            pipe.delete(tmp)
            runs = pipe.execute()[1]
        else:
            runs = self.r.zrevrangebyscore(
                Keys.RUNS, run_before, run_after, limit * (page - 1), limit)
        pipe = self.r.pipeline()
        for run in runs:
            pipe.hgetall(Keys.RUN.format(run))
        runs = pipe.execute()
        return ListModel.from_redis(runs, RunModel)

    def create_run(self, run_at=None, run_time=None, metadata=None):
        run_time = run_time or 0.0
        metadata = metadata or {}
        run_id = self.r.incr(Keys.NEXT_RUN)
        run_key = Keys.RUN.format(run_id)
        run_at = parse_date_ts(run_at)
        mapping = {
            Run.RUN_ID: run_id,
            Run.SKIPPED: 0,
            Run.FAILED: 0,
            Run.PASSED: 0,
            Run.RUN_TIME: run_time,
            Run.RUN_AT: run_at}
        pipe = self.r.pipeline()
        for k, v in metadata.items():
            mapping[Run.METADATA.format(k)] = v
            pipe.sadd(Keys.RUN_META.format(k, v), run_id)

        pipe.zadd(Keys.RUNS, run_id, run_at)
        pipe.hmset(name=run_key, mapping=mapping)
        pipe.sadd(Keys.PASSED_RUNS, run_id)
        pipe.execute()
        self.r.expire(run_key, self.max_age)
        return run_id

    def create_test(
        self, run_id, test_name, status, start_time, stop_time,
            metadata=None):
        metadata = metadata or {}
        test_id = self.r.incr(Keys.NEXT_TEST)
        test_key = Keys.TEST.format(test_id)
        run_key = Keys.RUN.format(run_id)
        stats_key = Keys.TEST_STATS.format(test_name)
        run_tests_key = Keys.RUN_TESTS.format(run_id)
        start_time = parse_date_ts(start_time)
        stop_time = parse_date_ts(stop_time)

        status = TEST_STATUSES.index(status)

        if self.r.exists(stats_key):
            index = self.r.hget(Keys.TEST_NAME_TO_INDEX, test_name)
        else:
            self.r.hmset(stats_key, {
                TestStats.FAILED: 0,
                TestStats.PASSED: 0,
                TestStats.SKIPPED: 0,
                TestStats.RUN_COUNT: 0})
            index = self.r.incr(Keys.TEST_NAME_COUNT, 1)
            self.r.hmset(Keys.TEST_NAME_TO_INDEX, {test_name: index})
            self.r.hmset(Keys.TEST_INDEX_TO_NAME, {index: test_name})

        pipe = self.r.pipeline()

        mapping = {
            Test.ID: test_id,
            Test.NAME: index,
            Test.STATUS: status,
            Test.START_TIME: start_time,
            Test.RUN_TIME: stop_time - start_time,
            Test.RUN_ID: run_id}

        for k, v in metadata.items():
            mapping[Test.METADATA.format(k)] = v
            test_meta_key = Keys.TEST_META.format(k, v)
            pipe.sadd(test_meta_key, test_id)

        pipe.hmset(name=test_key, mapping=mapping)

        pipe.hincrby(stats_key, TestStats.RUN_COUNT)
        pipe.sadd(run_tests_key, test_id)
        pipe.expire(run_tests_key, self.max_age)
        if status == TEST_STATUSES.index("passed"):
            pipe.hincrby(stats_key, TestStats.PASSED)
            pipe.hincrby(run_key, Run.PASSED)
            pipe.sadd(Keys.TESTS_PASSED, test_id)
        elif status == TEST_STATUSES.index("failed"):
            pipe.hincrby(run_key, Run.FAILED)
            pipe.hincrby(stats_key, TestStats.FAILED)
            pipe.sadd(Keys.FAILED_RUNS, run_id)
            pipe.srem(Keys.PASSED_RUNS, run_id)
            pipe.sadd(Keys.TESTS_FAILED, test_id)
        elif status == TEST_STATUSES.index("skipped"):
            pipe.hincrby(stats_key, TestStats.SKIPPED)
            pipe.hincrby(run_key, Run.SKIPPED)
            pipe.sadd(Keys.TESTS_SKIPPED, test_id)
        else:
            raise Exception("invalid status")

        pipe.zadd(Keys.TESTS, test_id, start_time)
        pipe.expire(test_key, self.max_age)
        pipe.execute()
        return test_id

    def get_run_by_id(self, id_):
        data = self.r.hgetall(Keys.RUN.format(id_)) or None
        if data is None:
            return data
        return RunModel.from_redis(data)

    def get_tests(
        self, run_after=None, run_before=None, limit=DEFAULT_LIMIT,
            page=DEFAULT_PAGE, status=None, **metadata):
        tmp = uuid4().get_hex()
        intersect_sets = [Keys.TESTS]
        intersect_sets += [
            Keys.TEST_META.format(k, v) for k, v in metadata.items()]
        if status == "passed":
            intersect_sets.append(Keys.TESTS_PASSED)
        elif status == "failed":
            intersect_sets.append(Keys.TESTS_FAILED)
        elif status == "skipped":
            intersect_sets.append(Keys.TESTS_SKIPPED)


        run_after = parse_date_ts(run_after) if run_after else "-inf"
        run_before = parse_date_ts(run_before) if run_before else "+inf"

        if len(intersect_sets) > 1:
            pipe = self.r.pipeline()
            pipe.zinterstore(tmp, intersect_sets, aggregate="max")
            pipe.zrevrangebyscore(
                tmp, run_before, run_after, limit * (page - 1), limit)
            pipe.expire(tmp, 3)
            tests = pipe.execute()[1]
        else:
            tests = self.r.zrevrangebyscore(
                Keys.TESTS, run_before, run_after, limit * (page - 1), limit)
        return self.get_tests_by_ids(tests)

    def get_test_by_id(self, test_id):
        test_key = Keys.TEST.format(test_id)
        if not self.r.exists(test_key):
            return None
        data = self.r.hgetall(test_key)
        data[Test.NAME] = self.r.hget(
            Keys.TEST_INDEX_TO_NAME, data.get(Test.NAME))
        data[Test.STATUS] = TEST_STATUSES[int(data.get(Test.STATUS))]
        return TestModel.from_redis(data)

    def get_tests_by_ids(self, test_ids):
        if not test_ids:
            return ListModel()
        pipe = self.r.pipeline()
        for test_id in test_ids:
            pipe.hgetall(Keys.TEST.format(test_id))
        tests = pipe.execute()
        indxs = [dic.get(Test.NAME) for dic in tests]
        for i, name in enumerate(self.r.hmget(Keys.TEST_INDEX_TO_NAME, indxs)):
            tests[i][Test.NAME] = name
        for test_id, test in zip(test_ids, tests):
            if test:
                test[Test.STATUS] = TEST_STATUSES[int(test.get(Test.STATUS))]
        return ListModel.from_redis(tests, TestModel)

    def get_tests_by_run_id(
        self, run_id, status=None, limit=DEFAULT_LIMIT, page=DEFAULT_PAGE,
            metadata=None):
        run_tests_key = Keys.RUN_TESTS.format(run_id)
        metadata = metadata or {}
        intersect_sets = [
            Keys.TEST_META.format(k, v) for k, v in metadata.items()]
        intersect_sets.append(run_tests_key)
        tmp = uuid4().get_hex()
        pipe = self.r.pipeline()

        if status == "passed":
            intersect_sets.append(Keys.TESTS_PASSED)
        elif status == "failed":
            intersect_sets.append(Keys.TESTS_FAILED)
        elif status == "skipped":
            intersect_sets.append(Keys.TESTS_SKIPPED)
        intersect_sets.append(Keys.TESTS)
        pipe.zinterstore(tmp, intersect_sets, aggregate="max")
        pipe.zrevrange(tmp, limit * (page - 1), limit * page)
        pipe.delete(tmp)
        return self.get_tests_by_ids(pipe.execute()[-2])

    def get_test_stats_by_name(self, test_name):
        stats_key = Keys.TEST_STATS.format(test_name)
        if not self.r.exists(stats_key):
            return None
        stats = self.r.hgetall(stats_key)
        stats[TestStats.TEST_NAME] = test_name
        return TestStatsModel.from_redis(stats)

    def get_test_name(self, test_id):
        test = self.get_test_by_id(test_id)
        if test is None:
            return None
        return test.test_name

    ###########################################################################
    # Attachments
    ###########################################################################
    #  Adding attachments is a two part call
    #  First reserve attachment number by calling get next attachment
    #  Then store attachment in external storage using attachment id returned
    #  from first call.  Use filename and external url to attach to run or test
    #  This allows redis to manage the ids without managing
    #  the storage.  External storage can be any key value store but having
    #  having no auth accessable urls is nice, otherwise all log access must go
    #  through the api which is slower

    # call first
    def get_next_attachment(self):
        return self.r.incr(Keys.NEXT_ATTACHMENT)

    def create_attachment(self, attachment_id, name, location):
        attachment_key = Keys.ATTACHMENT.format(attachment_id)
        mapping = {Attachment.NAME: name, Attachment.LOCATION: location}
        self.r.hmset(
            attachment_key,
            mapping={Attachment.NAME: name, Attachment.LOCATION: location})
        mapping[Attachment.ATTACHMENT_ID] = attachment_id
        self.r.lpush(Keys.ALL_ATTACHMENTS, attachment_id)
        return AttachmentModel.from_redis(mapping)

    # call second with a location to attachment
    def add_attachment_run(self, attachment_id, run_id):
        if not self.is_valid_run(run_id):
            return None
        self.r.sadd(Keys.RUN_ATTACHMENTS.format(run_id), attachment_id)

    # call second with a location to attachment
    def add_attachment_test(self, attachment_id, test_id):
        if not self.is_valid_test(test_id):
            return None
        self.r.sadd(Keys.TEST_ATTACHMENTS.format(test_id), attachment_id)

    def get_attachments_by_run_id(self, run_id):
        if not self.is_valid_run(run_id):
            return None
        key = Keys.RUN_ATTACHMENTS.format(run_id)
        attachment_ids = self.r.smembers(key)
        return self.get_attachments_by_ids(attachment_ids)

    def get_attachments_by_test_id(self, test_id):
        if not self.is_valid_test(test_id):
            return None
        key = Keys.TEST_ATTACHMENTS.format(test_id)
        attachment_ids = self.r.smembers(key)
        return self.get_attachments_by_ids(attachment_ids)

    def get_attachment_by_id(self, attachment_id):
        if not self.is_valid_attachment(attachment_id):
            return None
        attachment_key = Keys.ATTACHMENT.format(attachment_id)
        attachment = self.r.hgetall(attachment_key)
        attachment[Attachment.ATTACHMENT_ID] = attachment_id
        return AttachmentModel.from_redis(attachment)

    def get_attachments_by_ids(self, attachment_ids):
        attachment_ids = attachment_ids or []
        pipe = self.r.pipeline()
        for attachment_id in attachment_ids:
            pipe.hgetall(Keys.ATTACHMENT.format(attachment_id))
        attachments = pipe.execute()
        for i, attachment_id in enumerate(attachment_ids):
            attachments[i][Attachment.ATTACHMENT_ID] = attachment_id
        return ListModel.from_redis(attachments, AttachmentModel)

    def get_attachments(self, limit=DEFAULT_LIMIT, page=DEFAULT_PAGE):
        start = (page - 1) * limit
        end = start + limit - 1
        attachment_ids = self.r.lrange(Keys.ALL_ATTACHMENTS, start, end)
        return self.get_attachments_by_ids(attachment_ids)

    def is_valid_attachment(self, attachment_id):
        attachment_key = Keys.ATTACHMENT.format(attachment_id)
        return self.r.exists(attachment_key)

    def is_valid_test(self, test_id):
        test_key = Keys.TEST.format(test_id)
        return self.r.exists(test_key)

    def is_valid_run(self, run_id):
        run_key = Keys.RUN.format(run_id)
        return self.r.exists(run_key)

    def create_filter(self, name, regex):
        self.r.hset(Keys.FILTERS, name, regex)
        return FilterModel(name, regex)

    def get_filters(self):
        return FiltersModel.from_redis(self.r.hgetall(Keys.FILTERS))

    def get_filter(self, name):
        regex = self.r.hget(Keys.FILTERS, name)
        if regex is None:
            return FilterModel()
        return FilterModel(name=name, regex=regex)

    def has_filter(self, name):
        return self.r.hexists(Keys.FILTERS, name)
