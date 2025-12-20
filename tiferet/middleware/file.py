"""Tiferet File Middleware"""

# *** imports

# ** core
import os
from typing import Any

# ** app
from ..commands import TiferetError, const
from ..contracts import FileService

# *** classes

#* class: file_loader_middleware
class FileLoaderMiddleware(FileService):
    '''
    Middleware for loading files into the application.
    '''

    # * attribute: path
    path: str

    # * attribute: mode
    mode: str

    # * attribute: encoding
    encoding: str

    # * attribute: newline
    newline: str

    # * attribute: file
    file: Any

    # * init
    def __init__(self, path: str, mode: str = 'r', encoding: str = 'utf-8', newline: str = None):
        '''
        Initialize the FileLoaderMiddleware with a file path, mode, and encoding.
        
        :param path: The path to the file to load.
        :type path: str
        :param mode: The mode in which to open the file (default is 'r' for read).
        :type mode: str
        :param encoding: The encoding to use when reading the file (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter to use when opening the file (default is None).
        :type newline: str
        '''

        # Verify the file mode.
        self.verify_mode(mode)

        # Validate the encoding.
        self.verify_encoding(encoding)
        
        # Set the path, mode, and encoding for the file loader.
        self.mode = mode
        self.path = path
        self.encoding = encoding
        self.newline = newline

        # Set the file stream to None initially. It will be opened when the context is entered.
        self.file = None

    # * method: verify_file
    def verify_file(self, path: str):
        '''
        Verify that the file exists and is accessible.

        :param path: The path to the file to verify.
        :type path: str
        '''

        # Raise an error if the file does not exist.
        if not os.path.exists(path):
            raise TiferetError(
                const.FILE_NOT_FOUND_ID,
                f'File not found: {path}.',
                path=path
            )
        
        # Raise an error if the path is not a file.
        if not os.path.isfile(path):
            raise TiferetError(
                const.INVALID_FILE_ID,
                f'Path is not a file: {path}.',
                path=path
            )
        
    # * method: verify_mode
    def verify_mode(self, mode: str):
        '''
        Verify that the file mode is valid.

        :param mode: The mode in which to open the file.
        :type mode: str
        '''

        # Validate the file mode.
        valid_modes = ['r', 'w', 'a', 'rb', 'wb', 'ab']
        if mode not in valid_modes:
            raise TiferetError(
                const.INVALID_FILE_MODE_ID,
                f'Invalid file mode: {mode}. Valid modes include {str(valid_modes)}',
                mode=mode,
                modes=str(valid_modes)
            )
        
    # * method: verify_encoding
    def verify_encoding(self, encoding: str):
        '''
        Verify that the encoding is valid.

        :param encoding: The encoding to use when reading the file.
        :type encoding: str
        '''

        # Validate the encoding.
        if encoding not in ['utf-8', 'ascii', 'latin-1']:
            raise TiferetError(
                const.INVALID_ENCODING_ID,
                f'Invalid encoding: {encoding}. Supported encodings are: utf-8, ascii, latin-1.',
                encoding=encoding     
            )
        
    # * method: open_file
    def open_file(self):
        '''
        Open the file with the specified path, mode, and encoding. This method is called when the context is entered.
        
        :return: The opened file stream.
        :rtype: Any
        '''

        # Verify the file before opening it.
        self.verify_file(self.path)

        # Raise a RuntimeError if the file is already open to prevent multiple openings.
        if self.file is not None:
            raise TiferetError(
                const.FILE_ALREADY_OPEN_ID,
                f'File is already open: {self.path}.',
                path=self.path
            )
        
        # Open the file with the specified parameters.
        self.file = open(
            self.path, 
            mode=self.mode, 
            encoding=self.encoding,
            newline=self.newline
        )

    # * method: close_file
    def close_file(self):
        '''
        Close the file if it is open. This method is called when the context is exited.
        '''

        # Close the file if it is open and set the file attribute to None.
        if self.file is not None:
            self.file.close()
            self.file = None

    # * method: __enter__
    def __enter__(self):
        '''
        Enter the runtime context related to this object. This method is called when the with statement is executed.
        
        :return: The file loader instance itself, which can be used to access the opened file.
        :rtype: FileLoaderMiddleware
        '''

        # Open the file and return the file loader instance for use within the context. 
        # The opened file stream can be accessed via the 'file' attribute of this instance.
        self.open_file()
        return self
    
    # * method: __exit__
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Exit the runtime context and close the file if it is open. This method is called when the with statement block is exited.
        
        :param exc_type: The type of exception raised (if any).
        :param exc_value: The value of the exception raised (if any).
        :param traceback: The traceback of the exception raised (if any).
        '''

        # Close the file.
        self.close_file()