import six
from importlib import import_module
import pkgutil

import falcon

from myapp import api
from myapp.api.base import BaseAPI
from myapp.auth.client import AuthClient
from myapp.common.utils import get_config_value
from myapp.files.client import FilesClient
from myapp.redis.client import RedisClient


def get_routes(package):
    routes = []
    for _, modname, ispkg in pkgutil.walk_packages(
        path=package.__path__,
        prefix=package.__name__ + '.',
            onerror=lambda x: None):
        if not ispkg:
            module = import_module(modname)
            for k, cls in vars(module).items():
                if k.startswith("_") or not isinstance(cls, six.class_types):
                    continue
                if issubclass(cls, BaseAPI):
                    if getattr(cls, "route", False):
                        routes.append(cls)
    return routes

# monkeypatch to force application json on raised exceptions
falcon.Request.client_prefers = lambda self, media_types: "application/json"

identity_url = get_config_value("auth", "url")
files_username = get_config_value("auth", "username")
files_apikey = get_config_value("auth", "apikey")
files_url = get_config_value("files", "url")
temp_url_key = get_config_value("files", "temp_url_key")
index_prefix = get_config_value("files", "prefix")

routes = get_routes(api)
redis_client = RedisClient()
files_auth = AuthClient(identity_url, files_username, files_apikey)
files_client = FilesClient(
    url=files_url,
    auth_client=files_auth,
    temp_url_key=temp_url_key,
    container_prefix=index_prefix)


class RequireJSON(object):

    def process_request(self, req, resp):

        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


def handle_404(req, resp):
    BaseAPI.not_found()


app = falcon.API(media_type="application/json", middleware=[RequireJSON()])
for class_ in routes:
    app.add_route(class_.route, class_(redis_client, files_client))

app.add_sink(handle_404, '')
