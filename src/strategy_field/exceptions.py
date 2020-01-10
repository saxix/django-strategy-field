class StrategyNameError(ValueError):
    default_message = "Invalid value '%s': must be a valid python dotted name."

    def __init__(self, name, message=None):
        self.name = str(name)
        self.message = message or self.default_message

    def __str__(self):
        return self.message % self.name


class StrategyClassError(ValueError):
    default_message = "Invalid argument: '%s' is a invalid python name"

    def __init__(self, name, message=None):
        self.name = str(name)
        self.message = message or self.default_message

    def __str__(self):
        return self.message % self.name


class StrategyImportError(ImportError):
    pass

class StrategyAttributeError(AttributeError):
    default_message = 'Unable to import %(name)s. %(module)s does not have %(class_str)s attribute'

    def __init__(self, name, module, class_str, message=None):
        self.name = str(name)
        self.module = module
        self.class_str = class_str
        self.message = message or self.default_message

    def __str__(self):
        return self.message % (self.name, self.module, self.class_str)
