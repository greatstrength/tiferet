"""Tiferet File Middleware Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..file import FileLoaderMiddleware

# *** fixtures

# ** fixture: temp_text_file
@pytest.fixture
def temp_text_file(tmp_path):
    '''
    Fixture to create a temporary text file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary text file.
    :rtype: str
    '''
    
    # Create a temporary text file with sample content.
    file_path = tmp_path / 'test.txt'
    with open(file_path, 'w', encoding='utf-8') as fmw:
        fmw.write('Sample content')
    
    # Return the file path as a string.
    return str(file_path)

# ** fixture: file_loader_middleware
@pytest.fixture
def file_loader_middleware(temp_text_file: str) -> FileLoaderMiddleware:
    '''
    Fixture to create a FileLoaderMiddleware instance for reading.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    :return: A FileLoaderMiddleware instance.
    :rtype: FileLoaderMiddleware
    '''
    
    # Create and return a FileLoaderMiddleware instance.
    return FileLoaderMiddleware(path=temp_text_file, mode='r', encoding='utf-8')

# ** fixture: file_loader_middleware_write
@pytest.fixture
def file_loader_middleware_write(temp_text_file: str) -> FileLoaderMiddleware:
    '''
    Fixture to create a FileLoaderMiddleware instance for writing.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    :return: A FileLoaderMiddleware instance.
    :rtype: FileLoaderMiddleware
    '''
    
    # Create and return a FileLoaderMiddleware instance for writing.
    return FileLoaderMiddleware(path=temp_text_file, mode='w', encoding='utf-8')

# *** tests

# ** test: file_loader_middleware_instantiation
def test_file_loader_middleware_instantiation(temp_text_file: str):
    '''
    Test successful instantiation of a FileLoaderMiddleware object.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a temporary text file for testing.
    with FileLoaderMiddleware(path=temp_text_file) as fmw:
        
        # Verify the instance type and attributes.
        assert isinstance(fmw, FileLoaderMiddleware)
        assert fmw.mode == 'r'
        assert fmw.encoding == 'utf-8'
        assert fmw.file is not None

# ** test: file_loader_middleware_mode_write
def test_file_loader_middleware_mode_write(temp_text_file: str):
    '''
    Test instantiation of FileLoaderMiddleware with write mode.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a FileLoaderMiddleware instance for writing.
    with FileLoaderMiddleware(path=temp_text_file, mode='w') as fmw:
        
        # Verify the instance type and attributes.
        assert isinstance(fmw, FileLoaderMiddleware)
        assert fmw.mode == 'w'
        assert fmw.encoding == 'utf-8'
        assert fmw.file is not None

# ** test: file_loader_middleware_encoding_ascii
def test_file_loader_middleware_encoding_ascii(temp_text_file: str):
    '''
    Test instantiation of FileLoaderMiddleware with ASCII encoding.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a FileLoaderMiddleware instance with ASCII encoding.
    with FileLoaderMiddleware(path=temp_text_file, encoding='ascii') as fmw:
        
        # Verify the instance type and attributes.
        assert isinstance(fmw, FileLoaderMiddleware)
        assert fmw.mode == 'r'
        assert fmw.encoding == 'ascii'
        assert fmw.file is not None

# ** test: file_loader_middleware_instantiation_invalid_path
def test_file_loader_middleware_instantiation_invalid_path():
    '''
    Test instantiation of FileLoaderMiddleware with an invalid file path raises an error.
    '''
    
    # Attempt to create FileLoaderMiddleware with a non-existent file path.
    with pytest.raises(FileNotFoundError) as exc_info:
        FileLoaderMiddleware(path='non_existent.txt')
    
    # Verify the error message.
    assert 'File not found: non_existent.txt' in str(exc_info.value)

# ** test: file_loader_middleware_instantiation_invalid_mode
def test_file_loader_middleware_instantiation_invalid_mode(temp_text_file: str):
    '''
    Test instantiation of FileLoaderMiddleware with an invalid mode raises an error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Attempt to create FileLoaderMiddleware with an invalid mode.
    with pytest.raises(ValueError) as exc_info:
        FileLoaderMiddleware(path=temp_text_file, mode='x')
    
    # Verify the error message.
    assert 'Invalid file mode: x' in str(exc_info.value)

# ** test: file_loader_middleware_instantiation_invalid_encoding
def test_file_loader_middleware_instantiation_invalid_encoding(temp_text_file: str):
    '''
    Test instantiation of FileLoaderMiddleware with an invalid encoding raises an error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Attempt to create FileLoaderMiddleware with an invalid encoding.
    with pytest.raises(ValueError) as exc_info:
        FileLoaderMiddleware(path=temp_text_file, encoding='utf-16')
    
    # Verify the error message.
    assert 'Invalid encoding: utf-16' in str(exc_info.value)

# ** test: file_loader_middleware_runtime_error_on_already_open
def test_file_loader_middleware_runtime_error_on_already_open(temp_text_file: str):
    '''
    Test that attempting to open an already open file with FileLoaderMiddleware raises a RuntimeError.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Create a FileLoaderMiddleware instance and open the file.
    with FileLoaderMiddleware(path=temp_text_file) as fmw:
        
        # Attempt to open the file again within the same context.
        with pytest.raises(RuntimeError) as exc_info:
            fmw.open_file()
    
    # Verify the error message.
    assert f'File is already open: {temp_text_file}' in str(exc_info.value)

# ** test: file_loader_middleware_open_and_close_file
def test_file_loader_middleware_open_and_close_file(temp_text_file: str):
    '''
    Test that the FileLoaderMiddleware opens and closes the file correctly.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Create a FileLoaderMiddleware instance and open the file.
    fmw = FileLoaderMiddleware(path=temp_text_file)
    fmw.open_file()

    # Verify that the file is open.
    assert fmw.file is not None

    # Close the file.
    fmw.close_file()

    # Verify that the file is closed.
    assert fmw.file is None

# ** test: context_manager_read
def test_context_manager_read(file_loader_middleware: FileLoaderMiddleware, temp_text_file: str):
    '''
    Test the context manager for reading a file.

    :param file_loader_middleware: The FileLoaderMiddleware instance to test.
    :type file_loader_middleware: FileLoaderMiddleware
    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Use the context manager to read the file.
    with file_loader_middleware as fmw:
        content = fmw.file.read()
    
    # Verify the file content.
    assert content == 'Sample content'
    
    # Verify the file is closed after exiting the context.
    assert file_loader_middleware.file is None

# ** test: context_manager_write
def test_context_manager_write(temp_text_file: str):
    '''
    Test the context manager for writing to a file.

    :param file_loader_middleware_write: The FileLoaderMiddleware instance for writing.
    :type file_loader_middleware_write: FileLoaderMiddleware
    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Use the context manager to write to the file.
    with FileLoaderMiddleware(temp_text_file, mode='w') as fmw:
        fmw.file.write('New content')
    
    # Verify the file content.
    with FileLoaderMiddleware(temp_text_file, mode='r') as fmw:
        content = fmw.file.read()

    assert content == 'New content'
    
    # Verify the file is closed after exiting the context.
    assert fmw.file is None