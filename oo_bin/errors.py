class OOBinException(Exception):
    pass


class TunnelAlreadyStartedException(OOBinException):
    pass

class DependencyNotMetException(OOBinException):
    pass

class ConfigNotFoundException(OOBinException):
    pass
