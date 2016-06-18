from myapp.api.base import BaseAPI
from myapp.models.test import TestModel


class Tests(BaseAPI):
    route = "/tests"

    def on_get(self, req, resp):
        """
        @api {get} /tests Get Tests
        @apiName GetTests
        @apiGroup Tests
        @apiDescription Get a list of tests
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
        @apiParam (Parameters) {Integer{1-1000}} [limit=100] Limit runs per request
        @apiParam (Parameters) {Metadata} metadata All other params read as metadata key=value used to filter tests
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String="passed","failed","skipped"} status Status of test
        @apiSuccess (Response Body) {Integer} run_id Run ID, same at URL run_id
        @apiSuccess (Response Body) {String} start_time DateTimeStamp or test start time
        @apiSuccess (Response Body) {String} stop_time DateTimeStamp or test stop time
        @apiSuccess (Response Body) {String} test_name Name of test
        @apiSuccess (Response Body) {Integer} test_id Test ID
        @apiSuccess (Response Body) {Dictionary} metadata Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            [
                {
                    "status": "passed",
                    "run_id": "3",
                    "start_time": "2014-03-24T17:18:35+00:00",
                    "stop_time": "2014-03-24T17:18:35.060518+00:00",
                    "test_name": "somerepo.ClusterActionTest.test_do_detach_policy_missing_policy",
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
        limit = self.handle_limit(req.params.pop("limit", None))
        page = self.handle_page(req.params.pop("page", None))
        resp.data = self.redis.get_tests(
            limit=limit, page=page, **req.params).to_json()

    def on_post(self, req, resp):
        """
        @api {get} /tests Cretae Test
        @apiName CreateTest
        @apiGroup Tests
        @apiDescription Create a test and add to a run
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Metadata} metadata All other params read as metadata key=value used to filter tests
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String="passed","failed","skipped"} status Status of test
        @apiSuccess (Response Body) {Integer} run_id Run ID, same at URL run_id
        @apiSuccess (Response Body) {String} start_time DateTimeStamp or test start time
        @apiSuccess (Response Body) {String} stop_time DateTimeStamp or test stop time
        @apiSuccess (Response Body) {String} test_name Name of test
        @apiSuccess (Response Body) {Integer} test_id Test ID
        @apiSuccess (Response Body) {Dictionary} [metadata] Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            [
                {
                    "status": "passed",
                    "run_id": "3",
                    "start_time": "2014-03-24T17:18:35+00:00",
                    "stop_time": "2014-03-24T17:18:35.060518+00:00",
                    "test_name": "somerepo.ClusterActionTest.test_do_detach_policy_missing_policy",
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
        try:
            model = TestModel.from_json(req.stream.read())
        except:
            self.bad_request("Invalid Json in body of request.")

        self.handle_dict(model.metadata, "metadata", False)
        self.handle_string(model.start_time, "start_time")
        self.handle_string(model.stop_time, "stop_time")
        self.handle_run_id(model.run_id)
        self.handle_test_status(model.status)
        self.handle_string(model.test_name, "test_name")
        test_id = self.redis.create_test(
            run_id=model.run_id,
            test_name=model.test_name,
            status=model.status,
            start_time=model.start_time,
            end_time=model.end_time,
            metadata=model.metadata)
        model.test_id = test_id
        resp.data = model.to_json()


class Test(BaseAPI):
    route = "/tests/{test_id}"

    def on_get(self, req, resp, test_id):
        """
        @api {get} /tests/{test_id} Get Test by ID
        @apiName GetTest
        @apiGroup Tests
        @apiDescription Get test by ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String="passed","failed","skipped"} status Status of test
        @apiSuccess (Response Body) {Integer} run_id Run ID, same at URL run_id
        @apiSuccess (Response Body) {String} start_time DateTimeStamp or test start time
        @apiSuccess (Response Body) {String} stop_time DateTimeStamp or test stop time
        @apiSuccess (Response Body) {String} test_name Name of test
        @apiSuccess (Response Body) {Integer} test_id Test ID
        @apiSuccess (Response Body) {Dictionary} metadata Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "status": "passed",
                "run_id": "3",
                "start_time": "2014-03-24T17:18:35+00:00",
                "stop_time": "2014-03-24T17:18:35.060518+00:00",
                "test_name": "somerepo.ClusterActionTest.test_do_detach_policy_missing_policy",
                "test_id": "3517",
                "metadata": {
                    "tags": "worker-5"
                }
            }
        """
        test = self.redis.get_test_by_id(test_id)
        if test is None:
            self.not_found()
        resp.data = test.to_json()


class TestStats(BaseAPI):
    route = "/tests/{test_id}/stats"

    def on_get(self, req, resp, test_id):
        """
        @api {get} /tests/{test_id}/stats Get Test by test ID
        @apiName GetTestStatsByID
        @apiGroup Stats
        @apiDescription Get test stats by ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} failed Number of failed test runs
        @apiSuccess (Response Body) {String} passed Number of passed test runs
        @apiSuccess (Response Body) {String} skipped Number of skipped test runs
        @apiSuccess (Response Body) {String} run_count Number of times test ran
        @apiSuccess (Response Body) {String} test_name Test Name
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "failed": "1",
                "passed": "1107",
                "run_count": "1108",
                "skipped": "0",
                "test_name": "somerepo.ProfileTest.test_profile_find_by_name"
            }
        """
        test_name = self.redis.get_test_name(test_id)
        if test_name is None:
            self.not_found()
        stats = self.redis.get_test_stats_by_name(test_name)
        resp.data = stats.to_json()


class TestAttachments(BaseAPI):
    route = "/tests/{test_id}/attachments"

    def on_get(self, req, resp, test_id):
        """
        @api {get} /tests/{test_id}/attachments Get Attachments for test
        @apiName GetTestAttachments
        @apiGroup Attachments
        @apiDescription Get attachments by Test ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} test_id Test ID of test
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} attachment_id Attachment_id of attachment
        @apiSuccess (Response Body) {String} name Name of attachment
        @apiSuccess (Response Body) {String} location Location of attachment
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
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
        resp.data = self.redis.get_attachments_by_test_id(test_id).to_json()
