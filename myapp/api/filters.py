from myapp.api.base import BaseAPI
from myapp.models.filters import FilterModel


class Filters(BaseAPI):
    route = "/filters"

    def on_get(self, req, resp):
        """
        @api {get} /filters Get Filters
        @apiName GetFilters
        @apiGroup Filters
        @apiDescription Get a list of regex filters and names

        @apiUse all_calls
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse filters_response
        """
        resp.data = self.redis.get_filters().to_json()

    def on_post(self, req, resp):
        """
        @api {post} /filters Create Filter
        @apiName CreateFilter
        @apiGroup Filters
        @apiDescription Create a filter

        @apiUse all_calls
        @apiParam (Parameters) None
        @apiUse filter_resquest_body
        @apiUse filter_response

        """
        self._create_filter(req, resp, False)

    def on_put(self, req, resp):
        """
        @api {put} /filters Update Filter
        @apiName UpdateFilter
        @apiGroup Filters
        @apiDescription Updates a filter

        @apiUse all_calls
        @apiParam (Parameters) None
        @apiUse filter_resquest_body
        @apiUse filter_response
        """
        self._create_filter(req, resp, True)

    def _create_filter(self, req, resp, update):
        model = FilterModel.from_user(req.stream.read())
        self.handle_filter_regex(model.name, model.regex, update)
        resp.data = self.redis.create_filter(model.name, model.regex).to_json()


class GetFilter(BaseAPI):
    route = "/filters/{name}"

    def on_get(self, req, resp, name):
        """
        @api {get} /filters/{name} Get Filter by name
        @apiName GetFilter
        @apiGroup Filters
        @apiDescription Get a Filter by name

        @apiUse all_calls
        @apiParam (URL Variable) {String} name Filter name
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse filter_response
        """
        self.handle_filter_name(name, True)
        resp.data = self.redis.get_filter(name).to_json()
