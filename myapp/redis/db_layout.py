

class Keys(object):
    NEXT_RUN = "1"  # int incremented on run add
    NEXT_TEST = "2"  # int incremented on test add
    TEST_STATS = "3:{0}"  # hash table - with values in TestStats
    RUN = "4:{0}"  # hash table - with run info
    FAILED_RUNS = "5"  # set - run_id added if a failed test added
    PASSED_RUNS = "6"  # set - run added on create removed on run test failure
    RUNS = "7"  # sorted set - (run_count, timestamp) for date ranges
    RUN_META = "8:{0}:{1}"  # set - with run_id of run with metadata
    TEST = "9:{0}"  # Hash table - with test info
    TEST_META = "a:{0}:{1}"  # set - with metadata a:{key}:{value}
    TESTS = "b"  # sorted set - tests by timestamp
    RUN_TESTS = "c:{0}"  # list - list of test_ids for run {0}
    TEST_NAME_TO_INDEX = "d"  # hash - mapping for num to name name to num
    TEST_INDEX_TO_NAME = "e"  # hash - mapping for num to name name to num
    TEST_NAME_COUNT = "f"  # int - count of uniq test names
    RUN_ATTACHMENTS = "g:{0}"  # set - attachments for run
    NEXT_ATTACHMENT = "h"  # int - increment per attachment
    ATTACHMENT = "i:{0}"  # hash - attchment
    TEST_ATTACHMENTS = "j:{0}"  # set - attachments for test
    ATTACHMENT_REGEXS = "k"  # hash containing name: regex
    ALL_ATTACHMENTS = "l"  # list of attachments
    FILTERS = "n"  # hash filter name: regex


class TestStats(object):
    RUN_COUNT = "1"  # int - incremented on test add
    SKIPPED = "2"  # int - incremented on test add
    FAILED = "3"  # int - incremented on test add
    PASSED = "4"  # int - incremented on test add
    # string - not stored in db place holder for model
    TEST_NAME = "5"


class Run(object):
    RUN_ID = "1"
    SKIPPED = "2"  # int - count of skipped tests
    FAILED = "3"  # int - count of failed tests
    PASSED = "4"  # int - count of passed tests
    RUN_TIME = "5"  # float - seconds run took fl
    RUN_AT = "6"  # float - timestamp, seconds since 1970 time.time()
    METADATA = "7:{0}"  # string for metadata 7:{key} = value


class Test(object):
    NAME = "1"  # int - mapping to test_name
    ID = "2"  # int - count
    RUN_ID = "3"  # int - run id
    STATUS = "4"  # int - enum("success", "fail", "skip", "unknown")
    START_TIME = "5"  # float - timestamp, seconds since 1970
    RUN_TIME = "6"  # float - seconds test took
    METADATA = "7:{0}"  # string for metadata 7:{key} = value


class Attachment(object):
    NAME = "1"  # string - name of attachment
    LOCATION = "2"  # string - cloudfiles url

    ATTACHMENT_ID = "3"  # not in db placeholder for model
