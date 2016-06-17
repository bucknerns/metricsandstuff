from ConfigParser import SafeConfigParser
from datetime import datetime
from importlib import import_module
import os
import pkgutil
import six
import time

from dateutil.parser import parse

from myapp.api.base import BaseAPI

if six.PY3:
    import timezone
else:
    import pytz as timezone

config = None


def get_config():
    global config
    if config is None:
        config = SafeConfigParser()
        home_dir = os.getenv("VIRTUAL_ENV", os.path.expanduser("~"))
        config_path = "{0}/.metricsandstuff/api_config.ini".format(home_dir)
        if not os.path.exists(config_path):
            raise Exception(
                "Config at: {0} does not exist!".format(config_path))
        config.read(config_path)
    return config


def time_func(func):
    def new_func(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print "{0} ({1}, {2}) {3:.2f} seconds".format(
            func.__name__, args, kwargs, end - start)
        return result
    return new_func


def parse_date_datetime(obj=None):
    if obj is None:
        dt = datetime.utcnow()
    elif isinstance(obj, (float, int, long)):
        dt = datetime.fromtimestamp(float(obj), timezone.utc)
    elif isinstance(obj, six.string_types):
        try:
            float_obj = float(obj)
            if float_obj > 2007 and float_obj <= datetime.now().year:
                dt = parse(obj)

            dt = datetime.fromtimestamp(float(obj), timezone.utc)
        except:
            dt = parse(obj)
    elif isinstance(obj, datetime):
        dt = obj
    else:
        raise Exception("Unknown time format")
    dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    return dt


def parse_date_ts(obj=None):
    dt = parse_date_datetime(obj)
    if six.PY3:
        return dt.timestamp()
    return (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()


def parse_date_string(obj=None):
    dt = parse_date_datetime(obj)
    return dt.isoformat()


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


def get_config_value(section, key):
    c = get_config()
    try:
        return c.get(section, key)
    except:
        return None
