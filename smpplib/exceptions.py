#
# Exceptions
#


class UnknownCommandError(Exception):
    """Raised when unknown command ID is received"""


class ConnectionError(Exception):
    """Connection error"""


class UnbindFromServer(Exception):
    """Unbind from SMPP server"""


class PDUError(RuntimeError):
    """Error processing PDU"""


class MessageTooLong(ValueError):
    """Text too long to fit 255 SMS"""

