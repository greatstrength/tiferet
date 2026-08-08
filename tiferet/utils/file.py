"""Tiferet Utils File"""

# *** imports

# ** core
from pathlib import Path
from typing import IO, Any, Optional

# ** app
from ..interfaces.core import ServiceError
from ..interfaces.file import FileService

# *** constants

# ** constant: file_not_found_id
FILE_NOT_FOUND_ID = 'FILE_NOT_FOUND'

# ** constant: file_already_open_id
FILE_ALREADY_OPEN_ID = 'FILE_ALREADY_OPEN'

# ** constant: invalid_file_id
INVALID_FILE_ID = 'INVALID_FILE'

# ** constant: invalid_file_mode_id
INVALID_FILE_MODE_ID = 'INVALID_FILE_MODE'

# ** constant: invalid_encoding_id
INVALID_ENCODING_ID = 'INVALID_ENCODING'

# ** constant: valid_file_modes
VALID_FILE_MODES = (
    'r',
    'rb',
    'w',
    'wb',
    'a',
    'ab',
    'x',
    'xb',
    'r+',
    'rb+',
    'w+',
    'wb+',
    'a+',
    'ab+',
)

# ** constant: valid_encodings
VALID_ENCODINGS = (
    'utf-8',
    'ascii',
    'latin-1',
)

# *** utils

# ** util: file_loader
class FileLoader(FileService):
    '''
    Base utility for low-level file stream operations with validation and context support.
    Implements the FileService contract.
    '''

    # * attribute: path
    path: Path

    # * attribute: mode
    mode: str

    # * attribute: encoding
    encoding: Optional[str]

    # * attribute: newline
    newline: Optional[str]

    # * attribute: file
    file: Optional[IO[Any]]

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'r',
            encoding: Optional[str] = None,
            newline: Optional[str] = None,
            **kwargs,
        ):
        '''
        Initialize FileLoader with path and open parameters.

        :param path: File system path (str or Path).
        :type path: str | Path
        :param mode: File open mode.
        :type mode: str
        :param encoding: Text encoding for text modes.
        :type encoding: Optional[str]
        :param newline: Newline handling mode.
        :type newline: Optional[str]
        :param kwargs: Additional parameters (ignored).
        :type kwargs: dict
        '''

        # Set the file path as a Path object.
        self.path = Path(path)

        # Set the file mode.
        self.mode = mode

        # Set the encoding for text modes.
        self.encoding = encoding

        # Set the newline handling mode.
        self.newline = newline

        # Initialize the file stream to None.
        self.file = None

    # * method: verify_file (static)
    @staticmethod
    def verify_file(path: Path, mode: str = 'r'):
        '''
        Verify that the file or parent directory exists as appropriate.

        For write/append/exclusive modes, verifies the parent directory exists.
        For read modes, verifies the file itself exists.

        :param path: The file path to verify.
        :type path: Path
        :param mode: The file open mode (used to determine verification strategy).
        :type mode: str
        :raises ServiceError: If the file or its parent directory does not exist.
        '''

        # For write, append, or exclusive modes, verify the parent directory exists.
        if any(c in mode for c in ('w', 'a', 'x')):
            if not path.parent.exists():
                ServiceError.raise_for(
                    FileLoader,
                    FILE_NOT_FOUND_ID,
                    f'File not found: {path}.',
                    path=str(path),
                )

        # For read modes, verify the file itself exists.
        else:
            if not path.exists():
                ServiceError.raise_for(
                    FileLoader,
                    FILE_NOT_FOUND_ID,
                    f'File not found: {path}.',
                    path=str(path),
                )

    # * method: verify_mode
    def verify_mode(self):
        '''
        Validate the file mode string.

        :raises ServiceError: If the mode is not in the set of valid modes.
        '''

        # Raise an error if the mode is not valid.
        if self.mode not in VALID_FILE_MODES:
            ServiceError.raise_for(
                self,
                INVALID_FILE_MODE_ID,
                f'Invalid file mode: {self.mode}. '
                f'Valid modes include {", ".join(VALID_FILE_MODES)}.',
                mode=self.mode,
                modes=list(VALID_FILE_MODES),
            )

    # * method: verify_encoding
    def verify_encoding(self):
        '''
        Ensure encoding is provided when required for text modes.

        :raises ServiceError: If encoding is None for a text (non-binary) mode.
        '''

        # Raise an error if encoding is missing for a text mode.
        if 'b' not in self.mode and self.encoding is None:
            ServiceError.raise_for(
                self,
                INVALID_ENCODING_ID,
                f'Invalid encoding: {self.encoding}. '
                f'Supported encodings are: {", ".join(VALID_ENCODINGS)}.',
                encoding=self.encoding,
            )

    # * method: open_file
    def open_file(self) -> IO[Any]:
        '''
        Open the file stream if not already open.

        :return: The opened file stream.
        :rtype: IO[Any]
        :raises ServiceError: If the file is already open, the path is invalid,
            the mode is invalid, or encoding is missing for text modes.
        '''

        # Raise an error if the file is already open.
        if self.file is not None:
            ServiceError.raise_for(
                self,
                FILE_ALREADY_OPEN_ID,
                f'File is already open: {self.path}.',
                path=str(self.path),
            )

        # Verify the file path exists as appropriate for the mode.
        self.verify_file(self.path, self.mode)

        # Validate the file mode.
        self.verify_mode()

        # Validate the encoding for text modes.
        self.verify_encoding()

        # Open the file with the specified parameters.
        self.file = open(
            self.path,
            mode=self.mode,
            encoding=self.encoding,
            newline=self.newline,
        )

        # Return the opened file stream.
        return self.file

    # * method: close_file
    def close_file(self) -> None:
        '''
        Close the open file stream if present.
        '''

        # Close the file if it is open and reset the attribute.
        if self.file is not None:
            self.file.close()
            self.file = None

    # * method: __enter__
    def __enter__(self) -> IO[Any]:
        '''
        Enter the runtime context and open the file stream.

        :return: The opened file stream.
        :rtype: IO[Any]
        '''

        # Open and return the file stream.
        return self.open_file()

    # * method: __exit__
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Exit the runtime context and close the file stream.

        :param exc_type: The exception type (if any).
        :param exc_val: The exception value (if any).
        :param exc_tb: The exception traceback (if any).
        :return: False to propagate exceptions.
        :rtype: bool
        '''

        # Close the file stream.
        self.close_file()

        # Do not suppress exceptions.
        return False
