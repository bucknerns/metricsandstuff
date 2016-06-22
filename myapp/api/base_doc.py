"""
@apiDefine all_calls
@apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
"""


"""
@apiDefine metadata_params
@apiParam (Parameters) {Metadata} metadata
            All other params read as metadata key=value used to filter runs
"""


"""
@apiDefine attachment_response
@apiSuccess (Response Body) {ID} attachment_id Attachment_id of attachment
@apiSuccess (Response Body) {String} name Name of attachment
@apiSuccess (Response Body) {String} location Location of attachment
@apiSuccessExample Response Example:
{
    "attachment_id": 15,
    "name": "my_attachment.log",
    "location": "https://storage101.dfw1.clouddrive.com/v1/..."
}
"""


"""
@apiDefine attachments_response
@apiSuccess (Response Body) {ID} attachment_id Attachment_id of attachment
@apiSuccess (Response Body) {String} name Name of attachment
@apiSuccess (Response Body) {String} location Location of attachment
@apiSuccessExample Response Example:
[
    {
        "attachment_id": "1",
        "name": "cafe.master.log",
        "location": "https://storage101.dfw1.clouddrive.com/v1/..."
    },
    {
        "attachment_id": "2",
        "name": "cafe.master.log",
        "location": "https://storage101.dfw1.clouddrive.com/v1/..."
    }
]
"""


"""
@apiDefine pages
@apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
@apiParam (Parameters) {Integer{1-1000}} [limit=100]
    Limit attachments per request
"""


"""
@apiDefine no_request_body
@apiParam (Request Body) None
@apiParamExample Request Example:
    None
"""


"""
@apiDefine create_attachment_body
@apiParam (Request Body) {String} name Name of file
@apiParam (Request Body) {String} data Base64 encoded data
@apiParam (Request Body) {ID} [run_id] ID of run to attach file
@apiParam (Request Body) {ID} [test_id] ID of test to attach file
@apiParamExample Request Example:
{
    "name": "my_attachment.log",
    "data": "aGVsbG8gd29ybGQ=",
    "test_id": 1,
    "run_id": "1"
}
"""


"""
@apiDefine attachment_update_body
@apiParam (Request Body) {ID} attachment_id Attachment_id of attachment
@apiParam (Request Body) {String} [name] Name of file
@apiParam (Request Body) {String} [data] Base64 encoded data
@apiParam (Request Body) {ID} [run_id] ID of run to attach file
@apiParam (Request Body) {ID} [test_id] ID of test to attach file
@apiParamExample Request Example:
{
    "attachment_id": 15,
    "name": "my_attachment.log",
    "data": "aGVsbG8gd29ybGQ=",
    "test_id": 1,
    "run_id": "1"
}
"""


"""
@apiDefine attachment_filter_req_resp_body
@apiParam (Request Body) {List} list List of filter names
@apiParamExample Request Example:
[
    "somefilter_with_named_groups",
    "somefilter_with_groups",
    "somefilter_with_no_groups"
]
@apiSuccess (Response Body) {Dictionary} group_dict
    A dictionary based on named groups in regex
@apiSuccess (Response Body) {List} group_list
    A list of groups based on non named groups in regex
@apiSuccess (Response Body) {String} match A string based on regex match
@apiSuccessExample Response Example: type=None
[
    {
        "named_group": "text that doesn't support literal_eval or json.loads",
        "named_group2": {
            "supported": "json.loads or literal_eval"
        },
        "named_group3": [
            "another supported literal_eval/json.loads"
        ]
    },
    [
        "regex2 matched but only has non named groups",
        "group2",
        "group3"
    ],
    "regex3 match that had no groups returns a string match"
]
@apiSuccessExample Response Example: type=groupdict
[
    {
        "named_group": "text that doesn't support literal_eval or json.loads",
        "named_group2": {
            "supported": "json.loads or literal_eval"
        },
        "named_group3": [
            "another supported literal_eval/json.loads",
            "woo"
        ]
    },
    {},
    {}
]

@apiSuccessExample Response Example: type=groups
[
    [
        "matched text that doesn't support literal_eval or json.loads",
        {"supported": "json.loads or literal_eval"},
        ["another supported literal_eval/json.loads"],
    ],
    ["regex2 matched but only has non named groups", "group2", "group3"],
    []
]
@apiSuccessExample Response Example: type=match
[
    "matched text that doesn't support literal_eval or json.loads",
    "regex2 matched but only has non named groups:group2:group3",
    "regex3 match that had no groups returns a string match"
]
"""


"""
@apiDefine filter_response
@apiSuccess (Response Body) {String} regex Regex filter
@apiSuccess (Response Body) {String} name Name of filter
@apiSuccessExample Response Example:
{
    "regex": ".*",
    "name": "somefilter"
}
"""


"""
@apiDefine filters_response
@apiSuccess (Response Body) {String} regex Regex filter
@apiSuccess (Response Body) {String} name Name of filter
@apiSuccessExample Response Example:
[
    {
        "regex": ".*",
        "name": "somefilter"
    },
    {
        "regex": ".*",
        "name": "somefilter2"
    }
]
"""


"""
@apiDefine filter_resquest_body
@apiParam (Request Body) {String} regex Regex filter
@apiParam (Request Body) {String} name Name of filter
@apiParamExample Request Example:
{
    "regex": ".*",
    "name": "somefilter"
}
"""


"""
@apiDefine run_response
@apiSuccess (Response Body) {Integer} skipped Number of skipped tests
@apiSuccess (Response Body) {Integer} failed Number of failed tests
@apiSuccess (Response Body) {Integer} passed Number of passed tests
@apiSuccess (Response Body) {ID} run_id ID of run
@apiSuccess (Response Body) {String} run_at DateTimeStamp or run start time
@apiSuccess (Response Body) {Float} run_time Run time in seconds
@apiSuccess (Response Body) {Dictionary} metadata
    Dictionary containing metadata key value pairs
@apiSuccessExample Response Example:
{
    "skipped": 0,
    "run_id": 1,
    "run_at": "2016-06-08T03:26:29+00:00",
    "failed": 0,
    "run_time": 234785.27076625824,
    "passed": 0,
    "metadata": {
        "engine": "opencafe",
        "build_version": "2.1",
        "product": "cbs",
        "datacenter": "dfw1"
    }
}
"""


"""
@apiDefine runs_response
@apiSuccess (Response Body) {Integer} skipped Number of skipped tests
@apiSuccess (Response Body) {Integer} failed Number of failed tests
@apiSuccess (Response Body) {Integer} passed Number of passed tests
@apiSuccess (Response Body) {ID} run_id ID of run
@apiSuccess (Response Body) {String} run_at DateTimeStamp or run start time
@apiSuccess (Response Body) {Float} run_time Run time in seconds
@apiSuccess (Response Body) {Dictionary} metadata
    Dictionary containing metadata key value pairs
@apiSuccessExample Response Example:
[
    {
        "skipped": 1,
        "run_id": "1015",
        "run_at": "2016-06-08T03:26:29+00:00",
        "failed": 0,
        "run_time": 234785.27076625824,
        "passed": 1757,
        "metadata": {
            "engine": "opencafe",
            "product": "cbs",
            "build_version": "2.1",
            "datacenter": "dfw1"
        }
    },
    {
        "skipped": 2,
        "run_id": "964",
        "run_at": "2016-06-04T17:20:28+00:00",
        "failed": 1,
        "run_time": 193982.4073586464,
        "passed": 1755,
        "metadata": {
            "engine": "opencafe",
            "product": "compute",
            "build_version": "3.1",
            "datacenter": "ord"
        }
    }
]
"""

"""
@apiDefine create_run_body
@apiParam (Request Body) {String} [run_at] DateTimeStamp or run start time
@apiParam (Request Body) {Float} [run_time] Run time in seconds
@apiParam (Request Body) {Dictionary} [metadata]
    Dictionary containing metadata key value pairs
@apiParamExample Request Example:
{
    "run_at": "2016-06-08T03:26:29+00:00",
    "run_time": 234785.27076625824,
    "metadata": {
        "engine": "opencafe",
        "product": "cbs",
        "build_version": "2.1",
        "datacenter": "dfw1"
    }
}
"""


"""
@apiDefine test_status_param
@apiParam (Parameters) {String="passed","failed","skipped"} status
    Status of test
"""


"""
@apiDefine test_response
@apiSuccess (Response Body) {String="passed","failed","skipped"} status
    Status of test
@apiSuccess (Response Body) {ID} run_id Run ID, same at URL run_id
@apiSuccess (Response Body) {String} start_time
    DateTimeStamp or test start time
@apiSuccess (Response Body) {String} stop_time DateTimeStamp or test stop time
@apiSuccess (Response Body) {String} test_name Name of test
@apiSuccess (Response Body) {ID} test_id Test ID
@apiSuccess (Response Body) {Dictionary} metadata
    Dictionary containing metadata key value pairs
@apiSuccessExample Response Example:
{
    "status": "passed",
    "run_id": "3",
    "start_time": "2014-03-23T22:58:31+00:00",
    "stop_time": "2014-03-23T22:58:31.052204+00:00",
    "test_name": "somerepo.PolicyControllerTest.test_policy_update_normal",
    "test_id": "3518",
    "metadata": {
        "tags": "worker-7"
    }
}
"""


"""
@apiDefine tests_response
@apiSuccess (Response Body) {String="passed","failed","skipped"} status
    Status of test
@apiSuccess (Response Body) {ID} run_id Run ID, same at URL run_id
@apiSuccess (Response Body) {String} start_time
    DateTimeStamp or test start time
@apiSuccess (Response Body) {String} stop_time DateTimeStamp or test stop time
@apiSuccess (Response Body) {String} test_name Name of test
@apiSuccess (Response Body) {ID} test_id Test ID
@apiSuccess (Response Body) {Dictionary} metadata
    Dictionary containing metadata key value pairs
@apiSuccessExample Response Example:
[
    {
        "status": "passed",
        "run_id": "3",
        "start_time": "2014-03-24T17:18:35+00:00",
        "stop_time": "2014-03-24T17:18:35.060518+00:00",
        "test_name": "somerepo.ClusterActionTest.test_do_detach",
        "test_id": "3517",
        "metadata": {
            "tags": "worker-5"
        }
    },
    {
        "status": "passed",
        "run_id": "3",
        "start_time": "2014-03-23T22:58:31+00:00",
        "stop_time": "2014-03-23T22:58:31.052204+00:00",
        "test_name": "somerepo.PolicyControllerTest.test_policy_update_normal",
        "test_id": "3518",
        "metadata": {
            "tags": "worker-7"
        }
    }
]
"""


"""
@apiDefine create_test_body
@apiParam (Response Body) {String="passed","failed","skipped"} status
    Status of test
@apiParam (Response Body) {ID} run_id Run ID, same at URL run_id
@apiParam (Response Body) {String} start_time
    DateTimeStamp or test start time
@apiParam (Response Body) {String} stop_time DateTimeStamp or test stop time
@apiParam (Response Body) {String} test_name Name of test
@apiParam (Response Body) {Dictionary} [metadata]
    Dictionary containing metadata key value pairs. None nested data
@apiParamExample Request Example:
{
    "status": "passed",
    "run_id": "3",
    "start_time": "2014-03-23T22:58:31+00:00",
    "stop_time": "2014-03-23T22:58:31.052204+00:00",
    "test_name": "somerepo.PolicyControllerTest.test_policy_update_normal",
    "metadata": {
        "tags": "worker-7"
    }
}
"""


"""
@apiDefine stats_response
@apiSuccess (Response Body) {String} failed Number of failed test runs
@apiSuccess (Response Body) {String} passed Number of passed test runs
@apiSuccess (Response Body) {String} skipped Number of skipped test runs
@apiSuccess (Response Body) {String} run_count Number of times test ran
@apiSuccess (Response Body) {String} test_name Test Name
@apiSuccessExample Response Example:
{
    "failed": "1",
    "passed": "1107",
    "run_count": "1108",
    "skipped": "0",
    "test_name": "somerepo.ProfileTest.test_profile_find_by_name"
}

"""
