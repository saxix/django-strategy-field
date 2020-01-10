from inspect import isclass

from .utils import fqn, import_by_name


class Resolver:
    def __init__(self, **kwargs):
        pass

    def fqn(self, o):
        return fqn(o)

    def import_by_name(self, name):
        return import_by_name(name)

    def get_class(self, value):
        if not value:
            return value
        elif isinstance(value, str):
            return self.import_by_name(value)
        elif isclass(value):
            return value
        else:
            return type(value)

    def stringify(self, value):
        ret = []
        for v in value:
            if isinstance(v, str) and v:
                ret.append(v)
            else:
                ret.append(self.fqn(v))
        return ",".join(sorted(ret))


class ModuleMismatchError(ValueError):
    pass


class FixedPathResolver(Resolver):
    def __init__(self, prefix="", **kwargs):
        self.prefix = prefix
        super().__init__(**kwargs)

    def fqn(self, o):
        fullname = super().fqn(o)
        if not fullname.startswith(self.prefix):
            raise ModuleMismatchError("'{}' has not a valid module path.".format(o))
        return fullname

    def import_by_name(self, name):
        if not name.startswith(self.prefix):
            name = "{}.{}".format(self.prefix, name)
        return super().import_by_name(name)
