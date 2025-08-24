class FFError(Exception):
    pass


class FFConfigError(FFError):
    pass


class FFRegistryError(FFError):
    pass


class FFDependencyError(FFError):
    pass


class FFExecutionError(FFError):
    pass
