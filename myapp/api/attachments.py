import json

from myapp.api.base import BaseAPI
from myapp.models.attachment import AttachmentModel


class Attachments(BaseAPI):
    route = "/attachments"

    def on_get(self, req, resp):
        """
        @api {get} /attachments Get Attachments
        @apiName GetAttachments
        @apiGroup Attachments
        @apiDescription Get a list of attachments

        @apiUse all_calls
        @apiUse pages
        @apiUse no_request_body
        @apiUse attachments_response

        """
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

        @apiUse all_calls
        @apiUse create_attachment_body
        @apiUse attachment_response

        """
        self._create_attachment(req, resp, False)

    def on_put(self, req, resp):
        """
        @api {put} /attachments Update Attachment
        @apiName UpdateAttachments
        @apiGroup Attachments
        @apiDescription Update an attachemnt [and attach to a test or run]

        @apiUse all_calls
        @apiUse attachment_update_body
        @apiUse attachment_response
        """
        self._create_attachment(req, resp, True)

    def _create_attachment(self, req, resp, model, update=False):
        model = AttachmentModel.from_user(req.stream.read())
        self.handle_run_id(model.run_id, False)
        self.handle_test_id(model.test_id, False)
        if update:
            self.handle_attachment_id(model.attachment_id)
            existing_model = self.redis.get_attachment_by_id(
                model.attachment_id)
            model.name = (
                model.name if model.name is not None else existing_model.name)
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


class GetAttachmentByID(BaseAPI):
    route = "/attachments/{attachment_id}"

    def on_get(self, req, resp, attachment_id):
        """
        @api {get} /attachments/{attachment_id} Get Attachment by ID
        @apiName GetAttachment
        @apiGroup Attachments
        @apiDescription Get an attachment by attachment ID

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} attachment_id Attachment ID
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiUse attachment_response
        """
        self.handle_attachment_id(attachment_id)
        attachment = self.redis.get_attachment_by_id(attachment_id)
        resp.data = attachment.to_json()


class GetAttachment(BaseAPI):
    route = "/attachments/{attachment_id}/content"

    def on_get(self, req, resp, attachment_id):
        """
        @api {get} /attachments/{attachment_id}/content Get Attachment Content
        @apiName GetAttachmentContent
        @apiGroup Attachments
        @apiDescription Get an attachment's content by attachment ID
            Note: This call redirects to location URL

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} attachment_id Attachment ID
        @apiParam (Parameters) None
        @apiUse no_request_body
        @apiSuccess (Response Body) {Binary} Attachment Content
        @apiSuccessExample Response Example:
            hello world
        """
        self.handle_attachment_id(attachment_id)
        attachment = self.redis.get_attachment_by_id(attachment_id)
        self.redirect(attachment.location)


class FilterAttachment(BaseAPI):
    route = "/attachments/{attachment_id}/filter"

    def on_post(self, req, resp, attachment_id):
        """
        @api {post} /attachments/{attachment_id}/filter Filter Attachment
        @apiName FilterAttachment
        @apiGroup Attachments
        @apiDescription
            Get list of matches using one or more filters.
            Api call can return 3 possible match types: group dictionaries,
            group lists, or string matches. The call will attempt a
            literal_eval and a json.loads on the values of groups, if not
            sucessful it will return the string

        @apiUse all_calls
        @apiParam (URL Variable) {Integer} attachment_id Attachment ID
        @apiParam (Parameters) {String="groupdict","groups", "match"} [type]
            Type of matching to perform, overrides of auto discovery
        @apiUse attachment_filter_req_resp_body
        """
        self.handle_attachment_id(attachment_id)
        list_ = self.handle_list(
            self.handle_json(req.stream.read()), "request body", True, False)
        regexs = [
            self.redis.get_filter(
                self.handle_filter_name(name, True)).regex
            for name in list_]
        type_ = self.handle_filter_type(req.params.get("type"), False)
        resp.data = json.dumps(self.files.get_filter(
            attachment_id, regexs, type_))
