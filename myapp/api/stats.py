from myapp.api.base import BaseAPI


class TestStats(BaseAPI):
    route = "/stats/{test_name}"

    def on_get(self, req, resp, test_name):
        """
        @api {get} /status/{test_name} Get stats by test name
        @apiName GetStatsByName
        @apiGroup Stats
        @apiDescription Get stats by test name
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {String} test_name Name of test
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
        stats = self.redis.get_test_stats_by_name(test_name)
        if stats is None:
            self.not_found()
        resp.data = stats.to_json()
