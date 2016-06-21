import re
from base64 import b64decode

import falcon
import six

from myapp.common.constants import (
    RUN_STATUSES, TEST_STATUSES, DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT)
from myapp.common.utils import parse_date_string


class BaseAPI(object):
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
    def handle_run_status(cls, status, required=True):
        if required:
            cls.handle_required(status, "status")
        elif status is None:
            return None
        if status is not None and status not in RUN_STATUSES:
            cls.bad_request("'status' not in {0}.".format(RUN_STATUSES))
        return status

    @classmethod
    def handle_test_status(cls, status, required=True):
        if required:
            cls.handle_required(status, "status")
        elif status is None:
            return None
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
        if required:
            cls.handle_required(number, var_name)
        elif number is None:
            return None
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
        if required:
            cls.handle_required(string, var_name)
        elif string is None:
            return None
        if not isinstance(string, six.string_types):
            cls.bad_request("'{0}' must be a string".format(var_name))
        return string

    def handle_test_id(self, test_id, required=True):
        if required:
            self.handle_required(test_id, "test_id")
        elif test_id is None:
            return None
        if not self.redis.is_valid_test(test_id):
            self.bad_request("Invalid 'test_id'.")
        return test_id

    def handle_attachment_id(self, attachment_id, required=True):
        if required:
            self.handle_required(attachment_id, "attachment_id")
        elif attachment_id is None:
            return None
        if not self.redis.is_valid_attachment(attachment_id):
            self.bad_request("Invalid 'attachment_id'.")
        return attachment_id

    def handle_run_id(self, run_id, required=True):
        if required:
            self.handle_required(run_id, "run_id")
        elif run_id is None:
            return None
        if not self.redis.is_valid_run(run_id):
            self.bad_request("Invalid 'run_id'.")
        return run_id

    @classmethod
    def handle_float(cls, number, var_name, required=True):
        if required:
            cls.handle_required(number, var_name)
        elif number is None:
            return None
        try:
            return float(number)
        except ValueError:
            cls.bad_request("'{0}' must be a float.".format(var_name))

    @classmethod
    def handle_dict(cls, dic, var_name, required=False, nested=False):
        if required:
            cls.handle_required(dic, var_name)
        elif dic is None:
            return None
        if not isinstance(dic, dict):
            cls.bad_request("'{0}' must be a dictionary.".format(var_name))

        if not nested:
            for k, v in dic.items():
                if isinstance(v, (list, dict)):
                    cls.bad_request(
                        "Api does not support nested dictionary:'{0}'.".format(
                            var_name))
        return dic

    @classmethod
    def handle_date(cls, date, var_name, required=True):
        if required:
            cls.handle_required(date, var_name)
        elif date is None:
            return None
        cls.handle_string(date, var_name)
        try:
            return parse_date_string(date)
        except:
            cls._api.bad_request(
                "Date for var '{0}' is invalid.".format(var_name))

    @classmethod
    def handle_required(cls, var, var_name):
        if var is None:
            cls.bad_request("'{0}' is required.".format(var_name))
        return var

    @classmethod
    def handle_base64(cls, var, var_name, required=False):
        try:
            return b64decode(cls._api.handle_string(var, var_name, required))
        except:
            cls._API.bad_request("Invalid Base64 in data")

    @classmethod
    def handle_regex(self, regex, varname, required=True):
        self.handle_string(regex, varname)
        try:
            re.compile(regex)
            return regex
        except re.error:
            self.bad_request("Invalid regex '{0}'".format(varname))

    @classmethod
    def handle_filter(self, name, regex, exists):
        name = self.handle_string(name, "name")
        if exists != self.redis.has_filter(name):
            if exists:
                self.bad_request("Filter does not exist update failed")
            self.bad_request("Filter already exists create failed")
        return name, self.handle_regex(regex, "regex")
