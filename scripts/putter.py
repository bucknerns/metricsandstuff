import json
import logging
import os
import re

from multiprocess import Pool

from myapp.common.utils import parse_date_string, parse_date_ts
from myapp.elasticsearch.client import ElasticsearchClient
from myapp.api_client.client import APIClient
from myapp.models.test import TestModel
from myapp.models.run import RunModel

es_client = ElasticsearchClient()
api_client = APIClient()

def create_run(data):
    count = 0
    metadata = {
        "build_url": data.get("build_url"),
        "jenkins_status": d["jenkins_status"]}
    run_at = start_time = data.get("start_time")
    run_time = data.get("run_time")
    stop_time = data.get("stop_time")
    r = api_client.create_run(
        run_time=run_time, run_at=run_at, metadata=metadata)
    r2 = es_client.create_run(
        r.entity.run_id, run_at=run_at, run_time=run_time, metadata=metadata)
    if d["jenkins_status"] == "JENKINS_ERROR":
        print r, r.content
        return count
    test_regex = r'(?P<test_name>test_[^ ]*) \((?P<class_path>.*)\) \.\.\. (?P<status>.*)'
    module_regex = r'\tmodule name:\s*(?P<module_name>.*)'
    modules = re.findall(module_regex, data.get("stdout"))

    for test_name, class_path, status in re.findall(test_regex, data.get("stdout")):
        test_metadata = {}
        if modules:
            module = [module for module in modules if module in class_path][0]
            test_metadata["module_name"] = module
        test_metadata['test_class_path'] = class_path
        status = (
            "passed" if status == "ok" else
            "failed" if status == "FAIL"else
            "skipped" if status == "skipped" else status)
        test_metadata["framework_status"] = status
        if status not in ["passed", "failed", "skipped"]:
            status = "failed"

        r3 = api_client.create_test(
            run_id=r.entity.run_id,
            test_name=test_name,
            status=status,
            start_time=start_time,
            stop_time=stop_time,
            metadata=test_metadata)
        r4 = es_client.create_test(
            test_id=r3.entity.test_id,
            run_id=r.entity.run_id,
            test_name=test_name,
            status=status,
            start_time=start_time,
            stop_time=stop_time,
            metadata=test_metadata)
        count += 1
    api_client.create_attachment(
        name="stdout", data=data["stdout"], run_id=r.entity.run_id)
    api_client.create_attachment(
        name="cafe.master.log",
        data=open(os.path.expanduser("~/Downloads/cafe.master.log")).read(),
        run_id=r.entity.run_id)
    return count

data = [d.get("_source") for d in json.loads(open("records.json").read()).get("hits").get("hits")]
for d in data:
    d["stdout"] = "\n".join(d["message"])
    d["start_time"] = d["@buildTimestamp"]
    d["run_time"] = d["data"]["buildDuration"]/1000.0
    d["stop_time"] = d["@timestamp"]
    d["build_url"] = "{0}{1}".format(d["source_host"], d["data"]["url"])
    d["jenkins_status"] = "NORMAL" if d["data"]["buildVariables"] else "JENKINS_ERROR"
    del d["@version"]
    del d["@timestamp"]
    del d["source"]
    del d["source_host"]
    del d["message"]
    del d["data"]
    del d["@buildTimestamp"]

if __name__ == '__main__':
    # root = logging.getLogger()
    # root.addHandler(logging.StreamHandler())
    # root.setLevel(0)
    pool = Pool(20)
    test_count = sum(pool.map(create_run, data))

    print "Done: {} Runs / {} Tests uploaded".format(len(data), test_count)
