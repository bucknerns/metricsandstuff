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

        @apiUse all_calls
        @apiUse pages
        @apiUse metadata_params
        @apiUse no_request_body
        @apiUse tests_response

        """
        limit = self.handle_limit(req.params.pop("limit", None))
        page = self.handle_page(req.params.pop("page", None))
        resp.data = self.redis.get_tests(
            limit=limit, page=page, **req.params).to_json()

    def on_post(self, req, resp):
        """
        @api {post} /tests Create Test
        @apiName CreateTest
        @apiGroup Tests
        @apiDescription Create a test and add to a run

        @apiUse all_calls
        @apiUse create_test_body
        @apiUse test_response
        """
        model = TestModel.from_user(req.stream.read())
        self.handle_run_id(model.run_id)
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

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} test_id Test ID of test
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse test_response
        """
        test = self.redis.get_test_by_id(test_id)
        if test is None:
            self.not_found()
        resp.data = test.to_json()


class TestStats(BaseAPI):
    route = "/tests/{test_id}/stats"

    def on_get(self, req, resp, test_id):
        """
        @api {get} /tests/{test_id}/stats Get stats by test ID
        @apiName GetTestStatsByID
        @apiGroup Stats
        @apiDescription Get test stats by ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} test_id Test ID of test
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse stats_response

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
        @api {get} /tests/{test_id}/attachments Get Attachments for Test
        @apiName GetTestAttachments
        @apiGroup Attachments
        @apiDescription Get attachments by Test ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} test_id Test ID of test
        @apiUse no_request_body
        @apiUse attachments_response
        """
        resp.data = self.redis.get_attachments_by_test_id(test_id).to_json()
