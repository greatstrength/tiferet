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
    Gives one test a fresh temporary directory and a process-root log capture for that test run only, and returns what the test observes as plain data.

    It does not know the test, the phase, or the module run. The phase runtime arranges it, calls it, and closes it.
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
        '''

        # Nothing exists until arrange.
        self.directory = None
        self.handler = None
        self.root_level = None

    # * method: reject
    def _reject(self, message: str, cause: BaseException = None) -> None:
        '''
        Raise the local uncatalogued bad-call code.

        :param message: The rejection message.
        :type message: str
        :param cause: The originating exception, if any.
        :type cause: BaseException
        :return: None
        :rtype: None
        '''

        # Raise the local stage call code.
        ServiceError.raise_for(
            self,
            STAGE_CALL_INVALID,
            message=message,
            cause=cause,
        )

    # * method: require_arranged
    def _require_arranged(self) -> str:
        '''
        Return the stage directory, rejecting an unarranged stage.

        :return: The stage directory.
        :rtype: str
        '''

        # Reject when the stage has no directory.
        if self.directory is None:
            self._reject('The stage is not arranged.')

        # Return the directory.
        return self.directory

    # * method: require_segment
    def _require_segment(self, part: Any) -> str:
        '''
        Return one relative path segment, rejecting anything else.

        :param part: The candidate segment.
        :type part: Any
        :return: The segment.
        :rtype: str
        '''

        # Collect the truthy separators.
        separators = [sep for sep in ('/', os.sep, os.altsep) if sep]

        # Reject a non-string, a dot segment, an absolute path, or a separator.
        if (not isinstance(part, str)
                or part in ('', '.', '..')
                or os.path.isabs(part)
                or any(sep in part for sep in separators)):
            self._reject(f'{part!r} is not one relative path segment.')

        # Return the segment.
        return part

    # * method: arrange
    def arrange(self) -> None:
        '''
        Create the temporary directory and attach the log capture.

        :return: None
        :rtype: None
        '''

        # Reject a stage that is already arranged.
        if self.directory is not None or self.handler is not None:
            self._reject('The stage is already arranged.')

        # Create the temporary directory.
        self.directory = tempfile.mkdtemp(prefix=STAGE_PREFIX)

        # Build the capture handler at DEBUG.
        handler = BufferingHandler(sys.maxsize)
        handler.setLevel(logging.DEBUG)

        # Store the root level, lower the root to DEBUG, and attach the handler.
        root = logging.getLogger()
        self.root_level = root.level
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
        self.handler = handler

    # * method: close
    def close(self) -> None:
        '''
        Detach the capture, restore the root level, and remove the directory.

        :return: None
        :rtype: None
        '''

        # Detach the handler; it stays on the attribute.
        root = logging.getLogger()
        if self.handler is not None:
            root.removeHandler(self.handler)

        # Restore the root level once.
        if self.root_level is not None:
            root.setLevel(self.root_level)
            self.root_level = None

        # Clear the directory; a second close is a no-op.
        directory = self.directory
        self.directory = None
        if directory is None:
            return

        # Remove the directory.
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

        # Require an arranged stage and one segment per part.
        directory = self._require_arranged()
        for part in parts:
            self._require_segment(part)

        # Join the parts under the directory.
        return str(Path(directory, *parts))

    # * method: write
    def write(self, name: str, text: str) -> str:
        '''
        Write text as utf-8 bytes to one child of the directory.

        :param name: The child name.
        :type name: str
        :param text: The text to write.
        :type text: str
        :return: The written path string.
        :rtype: str
        '''

        # Require an arranged stage, one segment, and text.
        directory = self._require_arranged()
        self._require_segment(name)
        if not isinstance(text, str):
            self._reject('write takes text, not bytes or another value.')

        # Write the utf-8 bytes, overwriting any existing child.
        target = Path(directory, name)
        try:
            target.write_bytes(text.encode('utf-8'))
        except OSError as error:
            self._reject(f'{name} was not written: {error}', cause=error)

        # Return the written path string.
        return str(target)

    # * method: read
    def read(self, name: str) -> str:
        '''
        Read one child of the directory as utf-8 text.

        :param name: The child name.
        :type name: str
        :return: The decoded text.
        :rtype: str
        '''

        # Require an arranged stage and one segment.
        directory = self._require_arranged()
        self._require_segment(name)

        # Read and decode the child.
        try:
            return Path(directory, name).read_bytes().decode('utf-8')
        except (OSError, UnicodeDecodeError) as error:
            self._reject(f'{name} was not read: {error}', cause=error)

    # * method: exists
    def exists(self, name: str) -> bool:
        '''
        Report whether one child of the directory exists.

        :param name: The child name.
        :type name: str
        :return: True when the child exists.
        :rtype: bool
        '''

        # Require an arranged stage and one segment.
        directory = self._require_arranged()
        self._require_segment(name)

        # A missing child is False, not a rejection.
        return Path(directory, name).exists()

    # * method: records
    def records(self) -> List[Dict[str, Any]]:
        '''
        Return the captured records as plain dicts, in emission order.

        :return: Dicts with level, message, error, and logger.
        :rtype: List[Dict[str, Any]]
        '''

        # Require an arranged stage.
        self._require_arranged()

        # Return a new list of plain dicts in emission order.
        return [
            {
                'level': record.levelname,
                'message': record.getMessage(),
                'error': record.exc_info is not None,
                'logger': record.name,
            }
            for record in self.handler.buffer
        ]

    # * method: message
    def message(self, level: str, index: int) -> str:
        '''
        Return one captured message by level name and 0-based index.

        :param level: DEBUG, INFO, WARNING, ERROR, or CRITICAL.
        :type level: str
        :param index: The 0-based index within that level.
        :type index: int
        :return: The captured message.
        :rtype: str
        '''

        # Reject an unknown level.
        if level not in STAGE_LEVELS:
            self._reject(f'{level!r} is not one of {list(STAGE_LEVELS)}.')

        # Reject a non-int, bool, or negative index.
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            self._reject(f'{index!r} is not a 0-based index.')

        # Select that level's messages in order.
        messages = [
            record['message']
            for record in self.records()
            if record['level'] == level
        ]

        # Reject an index past the end.
        if index >= len(messages):
            self._reject(f'No {level} record at index {index}.')

        # Return the selected message.
        return messages[index]
