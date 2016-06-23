import six
import logging

from requests.packages.urllib3 import disable_warnings
import requests

from myapp.common.applogging import classproperty, get_object_namespace

disable_warnings()


def _safe_decode(text, incoming='utf-8', errors='replace'):
        if isinstance(text, six.text_type):
            return text

        return text.decode(incoming, errors)


def _log_transaction(func):
    def _wrapper(self, *args, **kwargs):
        level = 10
        logline = '{0} {1}'.format(args, kwargs)

        try:
            self._log.debug(_safe_decode(logline))
        except Exception as exception:
            self._log.info(
                'Exception occured while logging signature of calling'
                'method in http client')
            self._log.exception(exception)

        try:
            response = func(self, *args, **kwargs)
        except Exception as exception:
            self._log.critical('Call to Requests failed due to exception')
            self._log.exception(exception)
            raise exception

        request_body = ''
        if 'body' in dir(response.request):
            request_body = response.request.body
        elif 'data' in dir(response.request):
            request_body = response.request.data
        else:
            self._log.info(
                "Unable to log request body, neither a 'data' nor a "
                "'body' object could be found")

        request_params = ''
        request_url = response.request.url
        if 'params' in dir(response.request):
            request_params = response.request.params
        elif '?' in request_url:
            request_url, request_params = request_url.split('?', 1)

        logline = ''.join([
            '\n{0}\nREQUEST SENT\n{0}\n'.format('-' * 12),
            'request method..: {0}\n'.format(response.request.method),
            'request url.....: {0}\n'.format(request_url),
            'request params..: {0}\n'.format(request_params),
            'request headers.: {0}\n'.format(response.request.headers),
            'request body....: {0}\n'.format(request_body)])
        try:
            self._log.log(level, _safe_decode(logline))
        except Exception as exception:
            # Ignore all exceptions that happen in logging, then log them
            self._log.log(level, '\n{0}\nREQUEST INFO\n{0}\n'.format('-' * 12))
            self._log.exception(exception)

        logline = ''.join([
            '\n{0}\nRESPONSE RECEIVED\n{0}\n'.format('-' * 17),
            'response status..: {0}\n'.format(response),
            'response time....: {0}\n'.format(response.elapsed),
            'response headers.: {0}\n'.format(response.headers),
            'response body....: {0}\n'.format(response.content),
            '-' * 79])
        try:
            self._log.log(level, _safe_decode(logline))
        except Exception as exception:
            # Ignore all exceptions that happen in logging, then log them
            self._log.log(
                level, '\n{0}\nRESPONSE INFO\n{0}\n'.format('-' * 13))
            self._log.exception(exception)
        return response
    return _wrapper


class BaseHTTPClient(object):
    def __init__(self, url):
        self.headers = {}
        self.url = url

    @classproperty
    def _log(cls):
        return logging.getLogger(get_object_namespace(cls))

    @_log_transaction
    def request(self, method, url, **kwargs):
        headers = self.headers
        headers.update(kwargs.get("headers", {}))
        kwargs.update({"headers": headers})
        kwargs.update({"verify": False})
        return requests.request(method, url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def copy(self, url, **kwargs):
        return self.request('COPY', url, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.request('POST', url, data=data, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('HEAD', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request('PATCH', url, **kwargs)


class BaseRaxClient(BaseHTTPClient):
    def __init__(self, url, auth_client):
        super(BaseRaxClient, self).__init__(url)
        self._auth = auth_client

    @property
    def token(self):
        self.token = self._auth.token
        return self.headers.get("X-Auth-Token")

    @token.setter
    def token(self, value):
        self.headers["X-Auth-Token"] = value
