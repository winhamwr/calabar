"""calabar.log"""

import logging
import sys

def setup_logger(loglevel=logging.INFO, logfile=None):
    """
    Setup and return the logger for logging output. If ``logfile`` is not
    specified, ``stderr`` is used.

    Returns a :class:`logging.Logger` object.
    """
    logger = logging.getLogger('calabar')
    if logger.handlers:
        # Already configured
        return logger
    if logfile:
        if hasattr(logfile, "write"):
            log_file_handler = logging.StreamHandler(logfile)
        else:
            log_file_handler = logging.FileHandler(logfile)
        logger.addHandler(log_file_handler)

    return logger


def redirect_stdouts_to_logger(logger, loglevel=None):
    """Redirect :class:`sys.stdout` and :class:`sys.stderr` to a
    logging instance.

    :param logger: The :class:`logging.Logger` instance to redirect to.
    :param loglevel: The loglevel redirected messages will be logged as.

    Taken from the _`celery` project.

    .. _`celery`: http://ask.github.com/celery/
    """
    proxy = LoggingProxy(logger, loglevel)
    sys.stdout = proxy
    sys.stderr = proxy
    return proxy


class LoggingProxy(object):
    """Forward file object to :class:`logging.Logger` instance.

    :param logger: The :class:`logging.Logger` instance to forward to.
    :param loglevel: Loglevel to use when writing messages.

    Taken from the _`celery` project.

    .. _`celery`: http://ask.github.com/celery/
    """
    mode = "w"
    name = None
    closed = False
    loglevel = logging.INFO

    def __init__(self, logger, loglevel=None):
        self.logger = logger
        self.loglevel = loglevel or self.logger.level or self.loglevel
        self._safewrap_handlers()

    def _safewrap_handlers(self):
        """Make the logger handlers dump internal errors to
        ``sys.__stderr__`` instead of ``sys.stderr`` to circumvent
        infinite loops."""

        def wrap_handler(handler):

            class WithSafeHandleError(logging.Handler):

                def handleError(self, record):
                    exc_info = sys.exc_info()
                    try:
                        traceback.print_exception(exc_info[0], exc_info[1],
                                                  exc_info[2], None,
                                                  sys.__stderr__)
                    except IOError:
                        pass    # see python issue 5971
                    finally:
                        del(exc_info)

            handler.handleError = WithSafeHandleError().handleError

        return map(wrap_handler, self.logger.handlers)

    def write(self, data):
        """Write message to logging object."""
        if not self.closed:
            self.logger.log(self.loglevel, data)

    def writelines(self, sequence):
        """``writelines(sequence_of_strings) -> None``.

        Write the strings to the file.

        The sequence can be any iterable object producing strings.
        This is equivalent to calling :meth:`write` for each string.

        """
        map(self.write, sequence)

    def flush(self):
        """This object is not buffered so any :meth:`flush` requests
        are ignored."""
        pass

    def close(self):
        """When the object is closed, no write requests are forwarded to
        the logging object anymore."""
        self.closed = True

    def isatty(self):
        """Always returns ``False``. Just here for file support."""
        return False

    def fileno(self):
        return None