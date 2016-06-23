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

        @apiUse all_calls
        @apiUse pages
        @apiParam (Parameters) {String="passed","failed"} status
            Status of test based on failed test count
        @apiUse metadata_params
        @apiUse no_request_body
        @apiUse runs_response
        """
        status = self.handle_run_status(req.params.pop("status", None), False)
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

        @apiUse all_calls
        @apiParam (Parameters) None
        @apiUse create_run_body
        @apiUse run_response
        """
        model = RunModel.from_user(req.stream.read())
        run_id = self.redis.create_run(
            run_at=model.run_at,
            run_time=model.run_time,
            metadata=model.metadata)
        resp.data = self.redis.get_run_by_id(run_id).to_json()


class Run(BaseAPI):
    route = "/runs/{run_id}"

    def on_get(self, req, resp, run_id):
        """
        @api {get} /runs/{run_id} Get Run by ID
        @apiName GetRun
        @apiGroup Runs
        @apiDescription Get a run by ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} run_id Run ID of run
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse run_response
        """
        self.handle_run_id(run_id)
        resp.data = self.redis.get_run_by_id(run_id).to_json()


class TestsByRunID(BaseAPI):
    route = "/runs/{run_id}/tests"

    def on_get(self, req, resp, run_id):
        """
        @api {get} /runs/{run_id}/tests Get Tests by run ID
        @apiName GetRunTests
        @apiGroup Tests
        @apiDescription Get all tests for a given run ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} run_id Run ID of run
        @apiUse pages
        @apiParam (Parameters) {String} [name] Regex name filter
        @apiUse test_status_param
        @apiUse no_request_body
        @apiUse tests_response
        """
        tests = self.redis.get_tests_by_run_id(
            run_id=self.handle_run_id(run_id, True),
            status=self.handle_test_status(
                req.params.pop("status", None), False),
            limit=self.handle_limit(req.params.pop("limit", None)),
            page=self.handle_page(req.params.pop("page", None)),
            metadata=req.params)
        resp.data = tests.to_json()


class RunAttachments(BaseAPI):
    route = "/runs/{run_id}/attachments"

    def on_get(self, req, resp, run_id):
        """
        @api {get} /runs/{run_id}/attachments Get Attachments for Run
        @apiName GetRunAttachments
        @apiGroup Attachments
        @apiDescription Get attachments by run ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} run_id Run ID of run
        @apiUse no_request_body
        @apiUse attachments_response
        """
        resp.data = self.redis.get_attachments_by_run_id(run_id).to_json()
