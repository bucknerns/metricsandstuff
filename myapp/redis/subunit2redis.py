# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import sys
import os

from multiprocess import Pool
from oslo_config import cfg
from oslo_db import options
from pbr import version
from stevedore import enabled

from subunit2sql import exceptions
from subunit2sql import read_subunit as subunit
from myapp.redis.client import RedisClient
from myapp.elasticsearch.client import ElasticsearchClient
from myapp.common.utils import parse_date_ts, parse_date_string
from random import randint, choice
import requests
from base64 import b64encode
import json


CONF = cfg.CONF

SHELL_OPTS = [
    cfg.MultiStrOpt('subunit_files', positional=True,
                    help='list of subunit files to put into the database'),
    cfg.DictOpt('run_meta', short='r', default=None,
                help='Dict of metadata about the run(s)'),
    cfg.StrOpt('artifacts', short='a', default=None,
               help='Location of run artifacts'),
    cfg.BoolOpt('store_attachments', short='s', default=False,
                help='Store attachments from subunit streams in the DB'),
    cfg.StrOpt('run_id', short='i', default=None,
               help='Run id to use for the specified subunit stream, can only'
                    ' be used if a single stream is provided'),
    cfg.StrOpt('attr_regex', default='\[(.*)\]',
               help='The regex to use to extract the comma separated list of '
                    'test attributes from the test_id'),
    cfg.StrOpt('test_attr_prefix', short='p', default=None,
               help='An optional prefix to identify global test attrs '
                    'and treat it as test metadata instead of test_run '
                    'metadata'),
    cfg.StrOpt('run_at', default=None,
               help="The optional datetime string for the run was started, "
                    "If one isn't provided the date and time of when "
                    "subunit2sql is called will be used")
]

_version_ = version.VersionInfo('subunit2sql').version_string()


def cli_opts():
    for opt in SHELL_OPTS:
        CONF.register_cli_opt(opt)


def list_opts():
    """Return a list of oslo.config options available.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users.
    """
    return [('DEFAULT', copy.deepcopy(SHELL_OPTS))]


def parse_args(argv, default_config_files=None):
    cfg.CONF.register_cli_opts(options.database_opts, group='database')
    cfg.CONF(argv[1:], project='subunit2sql', version=_version_,
             default_config_files=default_config_files)


def running_avg(test, values, result):
    count = test.success
    avg_prev = test.run_time
    curr_runtime = subunit.get_duration(result['start_time'],
                                        result['end_time'])
    if isinstance(avg_prev, float):
        # Using a smoothed moving avg to limit the affect of a single outlier
        new_avg = ((count * avg_prev) + curr_runtime) / (count + 1)
        values['run_time'] = new_avg
    else:
        values['run_time'] = curr_runtime
    return values


def increment_counts(test, results):
    test_values = {'run_count': test.run_count + 1}
    status = results.get('status')
    if status == 'success':
        test_values['success'] = test.success + 1
        test_values = running_avg(test, test_values, results)
    elif status == 'fail':
        test_values['failure'] = test.failure + 1
    elif status == 'skip':
        test_values = {}
    else:
        msg = "Unknown test status %s" % status
        raise exceptions.UnknownStatus(msg)
    return test_values


def get_run_totals(results):
    success = len([x for x in results if results[x]['status'] == 'success'])
    fails = len([x for x in results if results[x]['status'] == 'fail'])
    skips = len([x for x in results if results[x]['status'] == 'skip'])
    totals = {
        'success': success,
        'fails': fails,
        'skips': skips,
    }
    return totals


def _get_test_attrs_list(attrs):
    if attrs:
        attr_list = attrs.split(',')
        test_attrs_list = [attr for attr in attr_list if attr.startswith(
            CONF.test_attr_prefix)]
        return test_attrs_list
    else:
        return None

db_client = None
es_client = None
attachment_log = b64encode(open(os.path.expanduser(
    "~/Downloads/cafe.master.log")).read())


def process_results(results):
    tester_names = ["tempest", "opencafe", "merlot"]
    builds = ["1.0", "1.1", "2.0", "2.1", "3.1", "3.3"]
    products = ["compute", "files", "cbs", "brm", "someuiproduct"]
    whattypeit = ["smoke", "regression", "blarg", "blerg", "smoke-prod"]
    datacenters = ["dfw1", "ord", "hkg", "syd"]
    max_end = max([
        parse_date_ts(data.get("end_time")) for data in results.values()])
    min_start = min([
        parse_date_ts(data.get("start_time")) for data in results.values()])
    run_time = (max_end - min_start) * randint(1, 5000)
    run_at = parse_date_string(randint(1333238400, 1465506042))
    metadata = CONF.run_meta or {}
    metadata["engine"] = choice(tester_names)
    metadata["build_version"] = choice(builds)
    metadata["product"] = choice(products)
    metadata["type"] = choice(whattypeit)
    metadata["datacenter"] = choice(datacenters)
    run_id = db_client.create_run(
        run_time=run_time,
        run_at=run_at,
        metadata=metadata)
    es_client.create_run(
        run_id=run_id,
        run_at=run_at,
        run_time=run_time,
        metadata=metadata)
    start_run_ts = parse_date_ts(run_at)
    end_run_ts = start_run_ts + run_time
    for test, data in results.items():
        start_time = randint(int(start_run_ts), int(end_run_ts))
        end_time = (
            start_time + parse_date_ts(data.get("end_time")) -
            parse_date_ts(data.get("start_time")))
        start_time = parse_date_string(start_time)
        end_time = parse_date_string(end_time)
        n = randint(0, 1600)
        if n == 1337:
            status = "failed"
        elif n == 42:
            status = "skipped"
        else:
            status = "passed"
        test_id = db_client.create_test(
            run_id=run_id,
            test_name=test,
            status=status,
            start_time=start_time,
            end_time=end_time,
            metadata=metadata)
        es_client.create_test(
            test_id=test_id,
            run_id=run_id,
            test_name=test,
            status=status,
            start_time=start_time,
            end_time=end_time,
            metadata=data.get("metadata"))
    attach_request = {
        "name": "cafe.master.log", "data": attachment_log, "run_id": run_id,
        "test_id": test_id}
    requests.post(
        "http://127.0.0.1/api/attachments", data=json.dumps(attach_request),
        headers={"Content-Type": "application/json"})


def get_extensions():
    def check_enabled(ext):
        return ext.plugin.enabled()
    return enabled.EnabledExtensionManager('subunit2sql.target',
                                           check_func=check_enabled)


def get_targets(extensions):
    try:
        targets = list(extensions.map(lambda ext: ext.plugin()))
    except RuntimeError:
        targets = []
    return targets


def main():
    global db_client
    global es_client
    cli_opts()

    extensions = get_extensions()
    parse_args(sys.argv)
    targets = get_targets(extensions)
    if CONF.subunit_files:
        if len(CONF.subunit_files) > 1 and CONF.run_id:
            print("You can not specify a run id for adding more than 1 stream")
            return 3
        streams = [subunit.ReadSubunit(open(s, 'r'),
                                       attachments=True,
                                       attr_regex=CONF.attr_regex,
                                       targets=targets)
                   for s in CONF.subunit_files]
    else:
        streams = [subunit.ReadSubunit(sys.stdin,
                                       attachments=CONF.store_attachments,
                                       attr_regex=CONF.attr_regex,
                                       targets=targets)]
    streams = [s.get_results() for s in streams]
    es_client = ElasticsearchClient()
    db_client = RedisClient()
    streams[0].pop("run_time")
    pool = Pool(20)
    pool.map(process_results, streams * 1000)
    regex = (
        '(?s)------------\n'
        'REQUEST SENT\n'
        '------------\n'
        '.*?request method..: (?P<request_method>.*?)\n'
        '.*?request url.....: (?P<request_url>.*?)\n'
        '.*?request params..: (?P<request_params>.*?)\n'
        '.*?request headers.: (?P<request_headers>.*?)\n'
        '.*?request body....: (?P<request_body>.*?)\n'
        '.*?-----------------\nRESPONSE RECEIVED\n-----------------\n'
        '.*?response status..: <Response \[(?P<response_status>.*?)\]>\n'
        '.*?response time....: (?P<response_time>.*?)\n'
        '.*?response headers.: (?P<response_headers>.*?)\n'
        '.*?response body....: (?P<response_body>.*?)\n'
        '-' * 79)
    filter_request = {"name": "opencafe_log_http", "regex": regex}
    requests.post(
        "http://127.0.0.1/api/filters", data=json.dumps(filter_request),
        headers={"Content-Type": "application/json"})

if __name__ == "__main__":
    sys.exit(main())
