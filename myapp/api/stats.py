from myapp.api.base import BaseAPI


class TestStats(BaseAPI):
    route = "/stats/{test_name}"

    def on_get(self, req, resp, test_name):
        """
        @api {get} /status/{test_name} Get stats by test name
        @apiName GetStatsByName
        @apiGroup Stats
        @apiDescription Get stats by test name

        @apiUse all_calls
        @apiParam (URL Variable) {String} test_name Name of test
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse stats_response
        """
        stats = self.redis.get_test_stats_by_name(test_name)
        if stats is None:
            self.not_found()
        resp.data = stats.to_json()
