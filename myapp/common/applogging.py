
def get_object_namespace(obj):
    try:
        return parse_class_namespace_string(str(obj.__mro__[0]))
    except:
        pass
    name = str(id(obj))
    try:
        name = "{0}_{1}".format(name, obj.__name__)
    except:
        pass
    return name


def parse_class_namespace_string(class_string):
    class_string = str(class_string)
    class_string = class_string.replace("'>", "")
    class_string = class_string.replace("<class '", "")
    return str(class_string)


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)
