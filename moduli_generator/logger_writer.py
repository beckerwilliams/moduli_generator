#!/usr/bin/env python
import concurrent.futures
import logging
import subprocess
import sys
from json import dump
from pathlib import PosixPath as Path
from typing import (Any, Dict, List)

from mariadb import (Error)

from config import (ISO_UTC_TIMESTAMP, default_config)
from db import MariaDBConnector

__all__ = ['ModuliGenerator', 'LoggerWriter', 'validate_subprocess_args']


class LoggerWriter:
    """
    A class that bridges a logger and writable interface.

    LoggerWriter acts as a writable stream that funnels written input to the
    specified logger, making it compatible with interfaces that expect a writable
    object (e.g., sys.stdout or sys.stderr redirection). This allows messages to
    be logged through standard Python logging instead of directly to the console.

    :ivar logger: The logging.Logger instance is used for logging messages.
    :type logger: logging.Logger
    :ivar level: The log level used when logging messages.
    :type level: int
    """

    def __init__(self, logger, level):
        """
        Initializes an instance of a logging class with a specified logger and logging level.

        :param logger: The logging instance to be used for log outputs.
        :param level: The logging level to determine what messages to log.
        """
        self.logger = logger
        self.level = level

    def write(self, message: str) -> int:
        """
        Writes a log message using the configured logging level.

        This method logs the given message using the specified logging level
        and returns the number of characters in the message. Empty or
        whitespace-only messages are excluded from logging.

        :param message: The message string to be logged.
        :type message: str

        :return: The length of the provided message.
        :rtype: int
        """
        if message.strip():  # Only log non-empty lines
            self.logger.log(self.level, message.strip())
        return len(message)

    def flush(self) -> None:
        """
        Flush the current state, performing any necessary cleanup or finalization.

        For this implementation, no actual flushing is needed since we're logging
        each message immediately, but this method is required to satisfy the
        file-like interface that the subprocess expects.

        :return: None
        :rtype: None
        """
        pass

    def fileno(self) -> int:
        """
        Return the file descriptor for the underlying stream.
        
        This method is required for compatibility with subprocess operations
        when using ProcessPoolExecutor. Since LoggerWriter doesn't have a real
        file descriptor, we return the file descriptor of sys.stderr as a fallback.
        
        :return: File descriptor number
        :rtype: int
        """
        return sys.stderr.fileno()