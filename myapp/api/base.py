import falcon
import six

from myapp.common.constants import (
    RUN_STATUSES, TEST_STATUSES, DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT)


class BaseAPI(object):
    """
    @apiDefine Version
    @apiVersion 0.0.0
    """
    route = None

    def __init__(self, redis_client, files_client):
        self.redis = redis_client
        self.files = files_client

    @staticmethod
    def bad_request(message):
        raise falcon.HTTPBadRequest(
            description=message, title=falcon.HTTP_400, code=400)

    @staticmethod
    def not_found(message="The requested resource does not exist"):
        raise falcon.HTTPNotFound(description=message, code=falcon.HTTP_404)

    @staticmethod
    def redirect(location):
        raise falcon.HTTPMovedPermanently(location)

    @classmethod
    def handle_run_status(cls, status):
        if status is not None and status not in RUN_STATUSES:
            cls.bad_request("'status' not in {0}.".format(RUN_STATUSES))
        return status

    @classmethod
    def handle_test_status(cls, status):
        if status and status not in TEST_STATUSES:
            cls.bad_request("'status' not in {0}.".format(TEST_STATUSES))
        return status

    @classmethod
    def handle_limit(cls, limit):
        if limit is None:
            limit = DEFAULT_LIMIT
        return cls.handle_int(limit, "limit", min_=1, max_=MAX_LIMIT)

    @classmethod
    def handle_page(cls, page):
        if page is None:
            page = DEFAULT_PAGE
        return cls.handle_int(page, "page", min_=1)

    @classmethod
    def handle_int(cls, number, var_name, min_=None, max_=None, required=True):
        if number is None:
            if required:
                cls.bad_request("'{0}' is required.".format(var_name))
            else:
                return number

        try:
            number = int(number)
        except ValueError:
            cls.bad_request("'{0}' must be an integer.".format(var_name))

        if max_ is not None:
            if number > max_:
                cls.bad_request(
                    "'{0}' must be less than or equal to {1}.".format(
                        var_name, max_))
        if min_ is not None:
            if number < min_:
                cls.bad_request(
                    "'{0}' must be greater than or equal to {1}.".format(
                        var_name, min_))
        return number

    @classmethod
    def handle_string(cls, string, var_name, required=True):
        if string is None:
            if required:
                cls.bad_request("'{0}' is required.".format(var_name))
            else:
                return string
        if not isinstance(string, six.string_types):
            cls.bad_request("'{0}' must be a string".format(var_name))

    def handle_test_id(self, test_id, required=True):
        if test_id is None:
            if required:
                self.bad_request("'test_id' is required.")
            else:
                return test_id
        if not self.redis.is_valid_test(test_id):
            self.bad_request("Invalid 'test_id'.")

    def handle_attachment_id(self, attachment_id, required=True):
        if attachment_id is None:
            if required:
                self.bad_request("'attachment_id' is required.")
            else:
                return attachment_id
        if not self.redis.is_valid_attachment(attachment_id):
            self.bad_request("Invalid 'attachment_id'.")

    def handle_run_id(self, run_id, required=True):
        if run_id is None:
            if required:
                self.bad_request("'run_id' is required.")
            else:
                return run_id
        if not self.redis.is_valid_run(run_id):
            self.bad_request("Invalid 'run_id'.")

    @classmethod
    def handle_float(cls, number, var_name, required=True):
        if number is None:
            if required:
                cls.bad_request("'{0}' is required.".format(var_name))
            else:
                return number
        try:
            number = float(number)
        except ValueError:
            cls.bad_request("'{0}' must be a float.".format(var_name))


    @classmethod
    def handle_dict(cls, dic, var_name, required=True, nested=False):
        if dic is None:
            if required:
                cls.bad_request("'{0}' is required.".format(var_name))
            else:
                return dic
        if not isinstance(dic, dict):
            cls.bad_request("'{0}' must be a dictionary.".format(var_name))

        if not nested:
            for k, v in dic.items():
                if isinstance(v, (list, dict)):
                    cls.bad_request(
                        "Api does not support nested dictionary:'{0}'.".format(
                            var_name))
