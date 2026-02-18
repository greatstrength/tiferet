"""Tiferet File Utility Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..file import FileLoader
from ...events import TiferetError, a

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

# ** fixture: file_loader
@pytest.fixture
def file_loader(temp_text_file: str) -> FileLoader:
    '''
    Fixture to create a FileLoader instance for reading.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    :return: A FileLoader instance.
    :rtype: FileLoader
    '''
    
    # Create and return a FileLoader instance.
    return FileLoader(path=temp_text_file, mode='r', encoding='utf-8')

# ** fixture: file_loader_write
@pytest.fixture
def file_loader_write(temp_text_file: str) -> FileLoader:
    '''
    Fixture to create a FileLoader instance for writing.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    :return: A FileLoader instance.
    :rtype: FileLoader
    '''
    
    # Create and return a FileLoader instance for writing.
    return FileLoader(path=temp_text_file, mode='w', encoding='utf-8')

# *** tests

# ** test: file_loader_instantiation
def test_file_loader_instantiation(temp_text_file: str):
    '''
    Test successful instantiation of a FileLoader object.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a temporary text file for testing.
    with FileLoader(path=temp_text_file) as fl:
        
        # Verify the instance type and attributes.
        assert isinstance(fl, FileLoader)
        assert fl.mode == 'r'
        assert fl.encoding == 'utf-8'
        assert fl.file is not None

# ** test: file_loader_mode_write
def test_file_loader_mode_write(temp_text_file: str):
    '''
    Test instantiation of FileLoader with write mode.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a FileLoader instance for writing.
    with FileLoader(path=temp_text_file, mode='w') as fl:
        
        # Verify the instance type and attributes.
        assert isinstance(fl, FileLoader)
        assert fl.mode == 'w'
        assert fl.encoding == 'utf-8'
        assert fl.file is not None

# ** test: file_loader_encoding_ascii
def test_file_loader_encoding_ascii(temp_text_file: str):
    '''
    Test instantiation of FileLoader with ASCII encoding.

    :param temp_text_file: The path to the temporary text file.
    '''

    # Create a FileLoader instance with ASCII encoding.
    with FileLoader(path=temp_text_file, encoding='ascii') as fl:
        
        # Verify the instance type and attributes.
        assert isinstance(fl, FileLoader)
        assert fl.mode == 'r'
        assert fl.encoding == 'ascii'
        assert fl.file is not None

# ** test: file_loader_instantiation_invalid_mode
def test_file_loader_instantiation_invalid_mode(temp_text_file: str):
    '''
    Test instantiation of FileLoader with an invalid mode raises an error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Attempt to create FileLoader with an invalid mode.
    with pytest.raises(TiferetError) as exc_info:
        FileLoader(path=temp_text_file, mode='x')
    
    # Verify the error message.
    assert exc_info.value.error_code == a.const.INVALID_FILE_MODE_ID
    assert 'Invalid file mode: x' in str(exc_info.value)
    assert exc_info.value.kwargs.get('mode') == 'x'

# ** test: file_loader_instantiation_invalid_encoding
def test_file_loader_instantiation_invalid_encoding(temp_text_file: str):
    '''
    Test instantiation of FileLoader with an invalid encoding raises an error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Attempt to create FileLoader with an invalid encoding.
    with pytest.raises(TiferetError) as exc_info:
        FileLoader(path=temp_text_file, encoding='utf-16')
    
    # Verify the error message.
    assert exc_info.value.error_code == a.const.INVALID_ENCODING_ID
    assert 'Invalid encoding: utf-16' in str(exc_info.value)
    assert exc_info.value.kwargs.get('encoding') == 'utf-16'

# ** test: file_loader_instantiation_invalid_path
def test_file_loader_instantiation_invalid_path():
    '''
    Test instantiation of FileLoader with an invalid file path raises an error.
    '''
    
    file_loader = FileLoader(path='non_existent.txt')

    # Attempt to create FileLoader with a non-existent file path.
    with pytest.raises(TiferetError) as exc_info:
        file_loader.open_file()
    
    # Verify the error message.
    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID
    assert 'File not found: non_existent.txt' in str(exc_info.value)
    assert exc_info.value.kwargs.get('path') == 'non_existent.txt'

# ** test: file_loader_runtime_error_on_already_open
def test_file_loader_runtime_error_on_already_open(temp_text_file: str):
    '''
    Test that attempting to open an already open file with FileLoader raises a RuntimeError.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Create a FileLoader instance and open the file.
    with FileLoader(path=temp_text_file) as fl:
        
        # Attempt to open the file again within the same context.
        with pytest.raises(TiferetError) as exc_info:
            fl.open_file()
    
    # Verify the error message.
    assert exc_info.value.error_code == a.const.FILE_ALREADY_OPEN_ID
    assert f'File is already open: {temp_text_file}' in str(exc_info.value)
    assert exc_info.value.kwargs.get('path') == temp_text_file

# ** test: file_loader_open_and_close_file
def test_file_loader_open_and_close_file(temp_text_file: str):
    '''
    Test that the FileLoader opens and closes the file correctly.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Create a FileLoader instance and open the file.
    fl = FileLoader(path=temp_text_file)
    fl.open_file()

    # Verify that the file is open.
    assert fl.file is not None

    # Close the file.
    fl.close_file()

    # Verify that the file is closed.
    assert fl.file is None

# ** test: context_manager_read
def test_context_manager_read(file_loader: FileLoader, temp_text_file: str):
    '''
    Test the context manager for reading a file.

    :param file_loader: The FileLoader instance to test.
    :type file_loader: FileLoader
    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Use the context manager to read the file.
    with file_loader as fl:
        content = fl.file.read()
    
    # Verify the file content.
    assert content == 'Sample content'
    
    # Verify the file is closed after exiting the context.
    assert file_loader.file is None

# ** test: context_manager_read_with_newline
def test_context_manager_read_with_newline(temp_text_file: str):
    '''
    Test the context manager for reading a file with newline parameter.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Create new file with specific newline characters.
    with open(temp_text_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('Line 1\nLine 2\nLine 3\n')
    
    # Use the context manager to read the file with newline parameter.
    with FileLoader(temp_text_file, mode='r', newline='\n') as fl:
        content = fl.file.readlines()

    # Verify the file content.
    assert content == ['Line 1\n', 'Line 2\n', 'Line 3\n']

# ** test: context_manager_write
def test_context_manager_write(temp_text_file: str):
    '''
    Test the context manager for writing to a file.

    :param file_loader_write: The FileLoader instance for writing.
    :type file_loader_write: FileLoader
    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: str
    '''
    
    # Use the context manager to write to the file.
    with FileLoader(temp_text_file, mode='w') as fl:
        fl.file.write('New content')
    
    # Verify the file content.
    with FileLoader(temp_text_file, mode='r') as fl:
        content = fl.file.read()

    assert content == 'New content'
    
    # Verify the file is closed after exiting the context.
    assert fl.file is None
