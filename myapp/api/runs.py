from myapp.api.base import BaseAPI
from myapp.models.run import RunModel


class Runs(BaseAPI):
    route = "/runs"

    def on_get(self, req, resp):
        """
        @api {get} /runs Get Runs
        @apiName GetRuns
        @apiGroup Runs
        @apiDescription Get a list of runs
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
        @apiParam (Parameters) {Integer{1-1000}} [limit=100] Limit runs per request
        @apiParam (Parameters) {Metadata} metadata All other params read as metadata key=value used to filter runs
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {Integer} skipped Number of skipped tests
        @apiSuccess (Response Body) {Integer} failed Number of failed tests
        @apiSuccess (Response Body) {Integer} passed Number of passed tests
        @apiSuccess (Response Body) {String} run_id ID of run
        @apiSuccess (Response Body) {String} run_at DateTimeStamp or run start time
        @apiSuccess (Response Body) {Float} run_time Run time in seconds
        @apiSuccess (Response Body) {Dictionary} metadata Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
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
        status = self.handle_run_status(req.params.pop("status", None))
        limit = self.handle_limit(req.params.pop("limit", None))
        page = self.handle_page(req.params.pop("page", None))
        resp.data = self.redis.get_runs(
            page=page, limit=limit, status=status, **req.params).to_json()

    def on_post(self, req, resp):
        """
        @api {post} /runs Create Run
        @apiName CreateRun
        @apiGroup Runs
        @apiDescription Create a new run
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) {String} [run_at] DateTimeStamp or run start time
        @apiParam (Request Body) {Float} [run_time] Run time in seconds
        @apiParam (Request Body) {Dictionary} [metadata] Dictionary containing metadata key value pairs
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
        @apiSuccess (Response Body) {Integer} skipped Number of skipped tests
        @apiSuccess (Response Body) {Integer} failed Number of failed tests
        @apiSuccess (Response Body) {Integer} passed Number of passed tests
        @apiSuccess (Response Body) {String} run_id ID of run
        @apiSuccess (Response Body) {String} run_at DateTimeStamp or run start time
        @apiSuccess (Response Body) {Float} run_time Run time in seconds
        @apiSuccess (Response Body) {Dictionary} metadata Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
           HTTP/1.1 200 OK
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
        try:
            model = RunModel.from_json(req.stream.read())
        except:
            self.bad_request("Invalid Json in body of request.")

        self.handle_dict(model.metadata, "metadata", False)
        self.handle_float(model.run_time, "run_time", required=False)
        self.handle_string(model.run_at, "run_at", required=False)

        run_id = self.redis.create_run(
            run_at=model.run_at,
            run_time=model.run_time,
            metadata=model.metadata)
        model.run_id = run_id
        model.skipped = 0
        model.failed = 0
        model.passed = 0
        resp.data = model.to_json()


class Run(BaseAPI):
    route = "/runs/{run_id}"

    def on_get(self, req, resp, run_id):
        """
        @api {get} /runs/{run_id} Get Run by ID
        @apiName GetRun
        @apiGroup Runs
        @apiDescription Get a run by ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} run_id Run ID of run
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {Integer} skipped Number of skipped tests
        @apiSuccess (Response Body) {Integer} failed Number of failed tests
        @apiSuccess (Response Body) {Integer} passed Number of passed tests
        @apiSuccess (Response Body) {String} run_id ID of run
        @apiSuccess (Response Body) {String} run_at DateTimeStamp or run start time
        @apiSuccess (Response Body) {Float} run_time Run time in seconds
        @apiSuccess (Response Body) {Dictionary} metadata Dictionary containing metadata key value pairs
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
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
            }
        """
        run = self.redis.get_run_by_id(run_id)
        if run is None:
            self.not_found()
        resp.data = run.to_json()


class TestsByRunID(BaseAPI):
    route = "/runs/{run_id}/tests"

    def on_get(self, req, resp, run_id):


        """
        @api {get} /runs/{run_id}/tests Get Tests by run ID
        @apiName GetRunTests
        @apiGroup Runs
        @apiDescription Get all tests for a given run ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} run_id Run ID of run
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
        status = self.handle_test_status(req.params.get("status"))
        tests = self.redis.get_tests_by_run_id(
            run_id, status, req.params.get("name"))
        if tests is None:
            self.not_found()
        resp.data = tests.to_json()


class RunAttachments(BaseAPI):
    route = "/runs/{run_id}/attachments"

    def on_get(self, req, resp, run_id):
        """
        @api {get} /runs/{run_id}/attachments Get Attachments for run
        @apiName GetRunAttachments
        @apiGroup Runs
        @apiDescription Get attachments by run ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} run_id Run ID of run
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
        resp.data = self.redis.get_attachments_by_run_id(run_id).to_json()
