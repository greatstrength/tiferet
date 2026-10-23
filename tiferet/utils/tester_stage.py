"""Tiferet Utils Stage"""

# *** imports

# ** core
import logging
import os
import shutil
import sys
import tempfile
from logging.handlers import BufferingHandler
from pathlib import Path
from typing import Any, Dict, List

# ** app
from ..interfaces.core import ServiceError
from ..interfaces.tester_stage import StageService

# *** constants

# ** constant: stage_call_invalid
STAGE_CALL_INVALID = 'STAGE_CALL_INVALID'

# ** constant: stage_levels
STAGE_LEVELS = (
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
)

# ** constant: stage_prefix
STAGE_PREFIX = 'tiferet-stage-'

# *** utils

# ** util: stage
class Stage(StageService):
    '''
    Gives one test a fresh temporary directory and a process-root log capture
    for that test run only, and returns what the test observes as plain data.

    It does not know the test, the phase, or the module run. The phase runtime
    arranges it, calls it, and closes it.
    '''

    # * attribute: directory
    directory: str | None

    # * attribute: handler
    handler: BufferingHandler | None

    # * attribute: root_level
    root_level: int | None

    # * init
    def __init__(self) -> None:
        '''
        Initialize an unarranged stage.

        :return: None.
        :rtype: None
        '''

        # Nothing exists until arrange.
        self.directory = None
        self.handler = None
        self.root_level = None

    # * method: reject
    def _reject(self, message: str, cause: BaseException = None) -> None:
        '''
        Raise the uncatalogued stage-call code.

        :param message: The defect message.
        :type message: str
        :param cause: The underlying exception, when there is one.
        :type cause: BaseException
        :return: None.
        :rtype: None
        '''

        # A bad stage call is infrastructural. The phase runtime catalogs it.
        ServiceError.raise_for(
            self,
            STAGE_CALL_INVALID,
            message=message,
            cause=cause,
        )

    # * method: require_arranged
    def _require_arranged(self) -> str:
        '''
        Return the directory, or raise when the stage is not arranged.

        :return: The directory string.
        :rtype: str
        '''

        # A closed or never-arranged stage has no directory.
        if self.directory is None:
            self._reject('The stage is not arranged.')
        return self.directory

    # * method: require_segment
    def _require_segment(self, part: Any) -> str:
        '''
        Return one relative path segment, or raise when it is not one.

        :param part: The candidate segment.
        :type part: Any
        :return: The segment.
        :rtype: str
        '''

        # Empty, dot, dot-dot, absolute, and separated parts would leave or blur the directory.
        separators = [
            sep
            for sep in ('/', os.sep, os.altsep)
            if sep
        ]
        if (
            not isinstance(part, str)
            or part in ('', '.', '..')
            or os.path.isabs(part)
            or any(sep in part for sep in separators)
        ):
            self._reject(f'{part!r} is not one relative path segment.')
        return part

    # * method: arrange
    def arrange(self) -> None:
        '''
        Create the temporary directory and attach the log capture.

        :return: None.
        :rtype: None
        '''

        # One stage arranges once.
        if self.directory is not None or self.handler is not None:
            self._reject('The stage is already arranged.')

        # A new unique directory. A suite must not depend on its parent or prefix.
        self.directory = tempfile.mkdtemp(prefix=STAGE_PREFIX)

        # Capture on the process root at DEBUG. Remember the level to restore.
        handler = BufferingHandler(sys.maxsize)
        handler.setLevel(logging.DEBUG)
        root = logging.getLogger()
        self.root_level = root.level
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
        self.handler = handler

    # * method: close
    def close(self) -> None:
        '''
        Detach the capture, restore the root level, and remove the directory.

        A second close is a no-op.

        :return: None.
        :rtype: None
        '''

        # Detach and restore first, so a directory error still leaves logging clean.
        root = logging.getLogger()
        if self.handler is not None:
            root.removeHandler(self.handler)
        if self.root_level is not None:
            root.setLevel(self.root_level)
            self.root_level = None

        # Remove the directory once. The captured records stay readable.
        directory = self.directory
        self.directory = None
        if directory is None:
            return
        try:
            shutil.rmtree(directory)
        except OSError as error:
            self._reject(f'The stage directory was not removed: {error}', cause=error)

    # * method: path
    def path(self, *parts: str) -> str:
        '''
        Join relative parts under the directory without creating anything.

        :param parts: Relative path parts. None returns the directory.
        :type parts: str
        :return: The joined path string.
        :rtype: str
        '''

        # Each part is one segment. Nothing is created.
        directory = self._require_arranged()
        for part in parts:
            self._require_segment(part)
        return str(Path(directory, *parts))

    # * method: write
    def write(self, name: str, text: str) -> str:
        '''
        Write text as utf-8 bytes to one child of the directory.

        An existing child is overwritten. Newlines are not translated.

        :param name: One path segment.
        :type name: str
        :param text: The text to write.
        :type text: str
        :return: The written path string.
        :rtype: str
        '''

        # Text only. No encoding argument and no bytes.
        directory = self._require_arranged()
        self._require_segment(name)
        if not isinstance(text, str):
            self._reject('write takes text, not bytes or another value.')

        # Write the utf-8 bytes, then return the path string.
        target = Path(directory, name)
        try:
            target.write_bytes(text.encode('utf-8'))
        except OSError as error:
            self._reject(f'{name} was not written: {error}', cause=error)
        return str(target)

    # * method: read
    def read(self, name: str) -> str:
        '''
        Read one child of the directory as utf-8 text.

        Newlines are not translated.

        :param name: One path segment.
        :type name: str
        :return: The text.
        :rtype: str
        '''

        # A missing or undecodable child is a failed call, not an empty string.
        directory = self._require_arranged()
        self._require_segment(name)
        try:
            return Path(directory, name).read_bytes().decode('utf-8')
        except (OSError, UnicodeDecodeError) as error:
            self._reject(f'{name} was not read: {error}', cause=error)

    # * method: exists
    def exists(self, name: str) -> bool:
        '''
        Report whether one child of the directory exists.

        :param name: One path segment.
        :type name: str
        :return: True when the child exists.
        :rtype: bool
        '''

        # A missing child is false. It is not a failed call.
        directory = self._require_arranged()
        self._require_segment(name)
        return Path(directory, name).exists()

    # * method: records
    def records(self) -> List[Dict[str, Any]]:
        '''
        Return the captured records as plain dicts, in emission order.

        :return: Dicts with level, message, error, and logger.
        :rtype: List[Dict[str, Any]]
        '''

        # A new list each call. A list stored earlier does not grow.
        self._require_arranged()
        return [
            {
                'level': record.levelname,
                'message': record.getMessage(),
                'error': record.exc_info is not None,
                'logger': record.name,
            }
            for record in list(self.handler.buffer)
        ]

    # * method: message
    def message(self, level: str, index: int) -> str:
        '''
        Return one captured message by level name and 0-based index.

        :param level: DEBUG, INFO, WARNING, ERROR, or CRITICAL.
        :type level: str
        :param index: The 0-based index within that level.
        :type index: int
        :return: The message string.
        :rtype: str
        '''

        # The level is a name. The index is a non-negative integer.
        if level not in STAGE_LEVELS:
            self._reject(f'{level!r} is not one of {list(STAGE_LEVELS)}.')
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            self._reject(f'{index!r} is not a 0-based index.')

        # Select that level's messages, in emission order.
        messages = [
            item['message']
            for item in self.records()
            if item['level'] == level
        ]
        if index >= len(messages):
            self._reject(f'No {level} record at index {index}.')
        return messages[index]
