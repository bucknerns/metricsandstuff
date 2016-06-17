from requests.packages.urllib3 import disable_warnings
import requests

disable_warnings()


class BaseHTTPClient(object):
    def __init__(self, url):
        self.s = requests.Session()
        self.s.verify = False
        self.url = url

    def request(self, method, url, **kwargs):
        self.token
        return self.s.request(method, url, **kwargs)

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
        return self.s.headers.get("X-Auth-Token")

    @token.setter
    def token(self, value):
        self.s.headers["X-Auth-Token"] = value
