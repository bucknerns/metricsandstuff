import json
import re

import falcon

from myapp.api.base import BaseAPI
from myapp.models.attachment import AttachmentModel, FilterModel


class Attachments(BaseAPI):
    route = "/attachments"

    def on_get(self, req, resp):
        """
        @api {get} /attachments Get Attachments
        @apiName GetAttachments
        @apiGroup Attachments
        @apiDescription Get a list of attachments
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
        @apiParam (Parameters) {Integer{1-1000}} [limit=100] Limit attachments per request
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} attachment_id Attachment_id of attachment
        @apiSuccess (Response Body) {String} name Name of attachment
        @apiSuccess (Response Body) {String} location Location of attachment
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            [{
                 "attachment_id": "1",
                 "name": "cafe.master.log",
                 "location": "https://storage101.dfw1.clouddrive.com/v1/..."
             },
             {
                 "attachment_id": "2",
                 "name": "cafe.master.log",
                 "location": "https://storage101.dfw1.clouddrive.com/v1/..."
            }]

        """
        resp.status = falcon.HTTP_200
        page = self.handle_page(req.params.get("page"))
        limit = self.handle_limit(req.params.get("limit"))
        resp.data = self.redis.get_attachments(
            limit=limit, page=page).to_json()

    def on_post(self, req, resp):
        """
        @api {post} /attachments Create Attachment
        @apiName CreateAttachments
        @apiGroup Attachments
        @apiDescription Create a new attachemnt [and attach to a test or run]
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
        @apiParam (Parameters) {Integer{1-1000}} [limit=100] Limit attachments per request
        @apiParam (Request Body) {String} name Name of file
        @apiParam (Request Body) {String} data Base64 encoded data
        @apiParam (Request Body) {Integer} [run_id] ID of run to attach file
        @apiParam (Request Body) {Integer} [test_id] ID of test to attach file
        @apiParamExample Request Example:
            {
                "name": "my_attachment.log",
                "data": "aGVsbG8gd29ybGQ=",
                "test_id": 1,
                "run_id": "1"
            }
        @apiSuccess (Response Body) {String} attachment_id Attachment_id of attachment
        @apiSuccess (Response Body) {String} name Name of attachment
        @apiSuccess (Response Body) {String} location Location of attachment
        @apiSuccessExample Response Example:
           HTTP/1.1 200 OK
            {
                 "attachment_id": 1,
                 "name": "my_attachment.log",
                 "location": "https://storage101.dfw1.clouddrive.com/v1..."
            }

        """
        self._create_attachment(req, resp, False)

    def on_put(self, req, resp):
        """
        @api {put} /attachments Update Attachment
        @apiName UpdateAttachments
        @apiGroup Attachments
        @apiDescription Update an attachemnt [and attach to a test or run]
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) {Integer{1-}} [page=1] Page number to start on
        @apiParam (Parameters) {Integer{1-1000}} [limit=100] Limit attachments per request
        @apiParam (Request Body) {String} attachment_id Attachment_id of attachment
        @apiParam (Request Body) {String} [name] Name of file
        @apiParam (Request Body) {String} [data] Base64 encoded data
        @apiParam (Request Body) {Integer} [run_id] ID of run to attach file
        @apiParam (Request Body) {Integer} [test_id] ID of test to attach file
        @apiParamExample Request Example:
            {
                "attachment_id": 15,
                "name": "my_attachment.log",
                "data": "aGVsbG8gd29ybGQ=",
                "test_id": 1,
                "run_id": "1"
            }
        @apiSuccess (Response Body) {String} attachment_id Attachment_id of attachment
        @apiSuccess (Response Body) {String} name Name of attachment
        @apiSuccess (Response Body) {String} location Location of attachment
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "attachment_id": 15,
                "name": "my_attachment.log",
                "location": "https://storage101.dfw1.clouddrive.com/v1/..."
            }

        """
        self._create_attachment(req, resp, True)

    def _create_attachment(self, req, resp, model, update=False):
        resp.status = falcon.HTTP_200
        model = AttachmentModel.from_user(req.stream.read())
        if update:
            self.handle_required(model.attachment_id)
            existing_model = self.redis.get_attachment_by_id(model.attachment_id)
            model.name = (
                model.name if model.name is not None else existing_model.name)
            model.data = (
                model.data if model.data is not None else
                self.files.get_attachment_by_id(model.attachment_id))
        else:
            self.handle_required(model.name, "name")
            self.handle_required(model.data, "data")
            model.attachment_id = self.redis.get_next_attachment()

        tempurl, response = self.files.create_attachment(
            model.attachment_id, model.data, model.name)

        if not response.ok:
            raise Exception("Failed in creating file")

        resp.data = self.redis.create_attachment(
            model.attachment_id, model.name, tempurl).to_json()

        if model.test_id is not None:
            self.redis.add_attachment_test(
                attachment_id=model.attachment_id,
                test_id=model.test_id)

        if model.run_id is not None:
            self.redis.add_attachment_run(
                attachment_id=model.attachment_id,
                run_id=model.run_id)


class AttachmentFilters(BaseAPI):
    route = "/attachments/filters"

    def on_get(self, req, resp):
        """
        @api {get} /attachments/filters Get Filters
        @apiName GetAttachmentFilters
        @apiGroup Filters
        @apiDescription Get a list of regex filters and names
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} regex Regex filter
        @apiSuccess (Response Body) {String} name Name of filter
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            [{
                "regex": ".*",
                "name": "somefilter"
            }]
        """
        resp.data = self.redis.get_attachment_filters().to_json()

    def on_post(self, req, resp):
        """
        @api {post} /attachments/filters Create Filter
        @apiName CreateFilter
        @apiGroup Filters
        @apiDescription Create a filter
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) {String} regex Regex filter
        @apiParam (Request Body) {String} name Name of filter
        @apiParamExample Request Example:
            {
                "regex": ".*",
                "name": "somefilter"
            }
        @apiSuccess (Response Body) {String} regex Regex filter
        @apiSuccess (Response Body) {String} name Name of filter
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "regex": ".*",
                "name": "somefilter"
            }
        """
        self._create_filter(req, resp, False)

    def on_put(self, req, resp):
        """
        @api {put} /attachments/filters Update Filter
        @apiName UpdateAttachmentFilters
        @apiGroup Filters
        @apiDescription Update a filter
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (Parameters) None
        @apiParam (Request Body) {String} regex Regex filter
        @apiParam (Request Body) {String} name Name of filter
        @apiParamExample Request Example:
            {
                "regex": ".*",
                "name": "somefilter"
            }
        @apiSuccess (Response Body) {String} regex Regex filter
        @apiSuccess (Response Body) {String} name Name of filter
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "regex": ".*",
                "name": "somefilter"
            }
        """
        self._create_filter(req, resp, True)

    def _create_filter(self, req, resp, update):
        resp.status = falcon.HTTP_200
        model = FilterModel.from_user(req.stream.read(), update)
        data = self.redis.create_filter(model.name, model.regex)
        resp.data = data.to_json()


class GetAttachmentByID(BaseAPI):
    route = "/attachments/{attachment_id}"

    def on_get(self, req, resp, attachment_id):
        """
        @api {get} /attachments/{attachment_id} Get Attachment by ID
        @apiName GetAttachment
        @apiGroup Attachments
        @apiDescription Get an attachment by attachment ID
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} attachment_id Attachment_id of attachment
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} attachment_id Attachment_id of attachment
        @apiSuccess (Response Body) {String} name Name of attachment
        @apiSuccess (Response Body) {String} location Location of attachment
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                 "attachment_id": "1",
                 "name": "cafe.master.log",
                 "location": "https://storage101.dfw1.clouddrive.com/v1/..."
             }
        """
        attachment = self.redis.get_attachment_by_id(attachment_id)
        if attachment is None:
            self.not_found()
        resp.data = attachment.to_json()


class GetAttachment(BaseAPI):
    route = "/attachments/{attachment_id}/content"

    def on_get(self, req, resp, attachment_id):
        """
        @api {get} /attachments/{attachment_id}/content Get Attachment Content by ID
        @apiName GetAttachmentContent
        @apiGroup Attachments
        @apiDescription Get an attachment's content by attachment ID
            Note: This call redirects to location URL
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} attachment_id Attachment_id of attachment
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {Binary} Attachment Content
        @apiSuccessExample Response Example:
            hello world
        """
        attachment = (
            self.redis.get_attachment_by_id(attachment_id) or self.not_found())
        self.redirect(attachment.location)


class GetFilter(BaseAPI):
    route = "/attachments/filters/{name}"

    def on_get(self, req, resp, name):
        """
        @api {get} /attachments/filters/{name} Get Filter by name
        @apiName GetAttachmentFilter
        @apiGroup Filters
        @apiDescription Get an Filter by name
        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {String} name Filter name
        @apiParam (Parameters) None
        @apiParam (Request Body) None
        @apiParamExample Request Example:
            None
        @apiSuccess (Response Body) {String} regex Regex filter
        @apiSuccess (Response Body) {String} name Name of filter
        @apiSuccessExample Response Example:
            HTTP/1.1 200 OK
            {
                "regex": ".*",
                "name": "somefilter"
            }
        """
        resp.data = self.redis.get_attachment_filter(name).to_json()


class FilterAttachment(BaseAPI):
    route = "/attachments/{attachment_id}/filter"

    def on_post(self, req, resp, attachment_id):
        """
        @api {post} /attachments/{attachment_id}/filter Filter Attachment
        @apiName FilterAttachment
        @apiGroup Attachments
        @apiDescription Get list of matches using one or more filters
            Api can return 3 possible match types: group dictionaries, group lists, or string matches
            Also the api call will attempt a literal_eval and a json.loads on the values of groups,
            if not sucessful it will return the string

        @apiHeader (Headers) {String} X-Auth-Token Identity Token with api access
        @apiParam (URL Variable) {Integer} attachment_id Attachment_id of attachment
        @apiParam (Parameters) {String="groupdict","groups", "match"} type Type of matching to perform, overrides auto discovery
        @apiParam (Request Body) {List} List of filter names
        @apiParamExample Request Example:
            [
                "somefilter_with_named_groups",
                "somefilter_with_groups",
                "somefilter_with_no_groups"
            ]
        @apiSuccess (Response Body) {Dictionary} group_dict A dictionary based on named groups in regex
        @apiSuccess (Response Body) {List} group_list A list of groups based on non named groups in regex
        @apiSuccess (Response Body) {String} group_list A string based on matched part of regex
        @apiSuccessExample Response Example: type=None
            HTTP/1.1 200 OK
            [
                {
                    "named_group": "matched text that doesn't support literal_eval or json.loads",
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
            HTTP/1.1 200 OK
            [
                {
                    "named_group": "matched text that doesn't support literal_eval or json.loads",
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
            HTTP/1.1 200 OK
            [
             ["matched text that doesn't support literal_eval or json.loads", {"supported": "json.loads or literal_eval"}, ["another supported literal_eval/json.loads"],
             ["regex2 matched but only has non named groups", "group2", "group3"],
             []
            ]
        @apiSuccessExample Response Example: type=match
            HTTP/1.1 200 OK
            [
                "matched text that doesn't support literal_eval or json.loads\nsupported: json.loads or literal_eval\n another supported literal_eval/json.loads",
                "regex2 matched but only has non named groups:group2:group3",
                "regex3 match that had no groups returns a string match"
            ]
        """
        if not self.redis.is_valid_attachment(attachment_id):
            self.not_found()
        try:
            list_ = json.loads(req.stream.read())
        except Exception as e:
            self.bad_request("Invalid json in request: {0}.".format(e))
        if not isinstance(list_, list) or not list_:
            self.bad_request("Body must contain a list of strings.")
        regexs = []
        for index, name in enumerate(list_):
            self.handle_string(name, "list_item[{0}]".format(index))
            model = self.redis.get_attachment_filter(name)
            if model is None:
                self.not_found(
                    "Attachment filter '{0}' does not exist.".format(name))
            regexs.append(model.regex)
        type_ = req.params.get("type")
        types = ["groupdict", "groups", "match"]
        if type_ is not None and type_ not in types:
            self.bad_request("'type' not in {0}.".format(types))
        resp.data = json.dumps(self.files.get_attachment_filter(
            attachment_id, regexs, type_))
