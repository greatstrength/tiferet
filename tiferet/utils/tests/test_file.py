"""Tiferet Utils File Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..file import FileLoader
from ...events import a
from ...events.settings import TiferetError

# *** fixtures

# ** fixture: temp_text_file
@pytest.fixture
def temp_text_file(tmp_path):
    '''
    Fixture to create a temporary text file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary text file.
    :rtype: pathlib.Path
    '''

    # Create a temporary text file with sample content.
    file_path = tmp_path / 'test.txt'
    file_path.write_text('Sample content', encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: file_loader_read
@pytest.fixture
def file_loader_read(temp_text_file) -> FileLoader:
    '''
    Fixture to create a FileLoader instance for reading.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    :return: A FileLoader instance configured for reading.
    :rtype: FileLoader
    '''

    # Create and return a FileLoader instance for reading.
    return FileLoader(path=temp_text_file, mode='r', encoding='utf-8')

# ** fixture: file_loader_write
@pytest.fixture
def file_loader_write(temp_text_file) -> FileLoader:
    '''
    Fixture to create a FileLoader instance for writing.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    :return: A FileLoader instance configured for writing.
    :rtype: FileLoader
    '''

    # Create and return a FileLoader instance for writing.
    return FileLoader(path=temp_text_file, mode='w', encoding='utf-8')

# *** tests

# ** test: file_loader_open_read_close_cycle
def test_file_loader_open_read_close_cycle(file_loader_read: FileLoader):
    '''
    Test successful open, read, and close cycle.

    :param file_loader_read: The FileLoader instance for reading.
    :type file_loader_read: FileLoader
    '''

    # Open the file stream.
    stream = file_loader_read.open_file()

    # Read the content.
    content = stream.read()

    # Verify the content matches.
    assert content == 'Sample content'

    # Close the file.
    file_loader_read.close_file()

    # Verify the file stream is cleared.
    assert file_loader_read.file is None

# ** test: file_loader_context_manager_read
def test_file_loader_context_manager_read(file_loader_read: FileLoader):
    '''
    Test context manager usage for reading a file.

    :param file_loader_read: The FileLoader instance for reading.
    :type file_loader_read: FileLoader
    '''

    # Use the context manager to read the file.
    with file_loader_read as f:
        content = f.read()

    # Verify the content matches.
    assert content == 'Sample content'

    # Verify the file stream is closed after exiting the context.
    assert file_loader_read.file is None

# ** test: file_loader_context_manager_write
def test_file_loader_context_manager_write(temp_text_file):
    '''
    Test context manager usage for writing to a file.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    '''

    # Write new content via context manager.
    with FileLoader(path=temp_text_file, mode='w', encoding='utf-8') as f:
        f.write('New content')

    # Read back and verify the content.
    with FileLoader(path=temp_text_file, mode='r', encoding='utf-8') as f:
        content = f.read()

    # Verify the written content.
    assert content == 'New content'

# ** test: file_loader_invalid_mode
def test_file_loader_invalid_mode(temp_text_file):
    '''
    Test that an invalid file mode raises INVALID_FILE_MODE error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    '''

    # Create a FileLoader with an invalid mode.
    loader = FileLoader(path=temp_text_file, mode='z', encoding='utf-8')

    # Attempt to open the file.
    with pytest.raises(TiferetError) as exc_info:
        loader.open_file()

    # Verify the error code and kwargs.
    assert exc_info.value.error_code == a.const.INVALID_FILE_MODE_ID
    assert exc_info.value.kwargs.get('mode') == 'z'

# ** test: file_loader_missing_encoding_text_mode
def test_file_loader_missing_encoding_text_mode(temp_text_file):
    '''
    Test that missing encoding in text mode raises INVALID_ENCODING error.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    '''

    # Create a FileLoader in text mode without encoding.
    loader = FileLoader(path=temp_text_file, mode='r', encoding=None)

    # Attempt to open the file.
    with pytest.raises(TiferetError) as exc_info:
        loader.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.INVALID_ENCODING_ID

# ** test: file_loader_already_open
def test_file_loader_already_open(file_loader_read: FileLoader):
    '''
    Test that opening an already-open file raises FILE_ALREADY_OPEN error.

    :param file_loader_read: The FileLoader instance for reading.
    :type file_loader_read: FileLoader
    '''

    # Open the file via context manager.
    with file_loader_read as f:

        # Attempt to open again.
        with pytest.raises(TiferetError) as exc_info:
            file_loader_read.open_file()

    # Verify the error code and kwargs.
    assert exc_info.value.error_code == a.const.FILE_ALREADY_OPEN_ID
    assert exc_info.value.kwargs.get('path') is not None

# ** test: file_loader_file_not_found_read
def test_file_loader_file_not_found_read(tmp_path):
    '''
    Test that reading a non-existent file raises FILE_NOT_FOUND error.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a FileLoader pointing to a non-existent file.
    loader = FileLoader(path=tmp_path / 'does_not_exist.txt', mode='r', encoding='utf-8')

    # Attempt to open the file.
    with pytest.raises(TiferetError) as exc_info:
        loader.open_file()

    # Verify the error code and kwargs.
    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID
    assert 'does_not_exist.txt' in exc_info.value.kwargs.get('path', '')

# ** test: file_loader_missing_parent_dir_write
def test_file_loader_missing_parent_dir_write(tmp_path):
    '''
    Test that writing to a file with a non-existent parent directory raises FILE_NOT_FOUND error.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a FileLoader pointing to a path with a missing parent directory.
    loader = FileLoader(
        path=tmp_path / 'nonexistent_dir' / 'file.txt',
        mode='w',
        encoding='utf-8',
    )

    # Attempt to open the file.
    with pytest.raises(TiferetError) as exc_info:
        loader.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID

# ** test: file_loader_binary_mode_no_encoding
def test_file_loader_binary_mode_no_encoding(temp_text_file):
    '''
    Test that binary mode does not require encoding.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    '''

    # Create a FileLoader in binary read mode without encoding.
    loader = FileLoader(path=temp_text_file, mode='rb', encoding=None)

    # Open, read, and close.
    with loader as f:
        content = f.read()

    # Verify the content is bytes.
    assert isinstance(content, bytes)
    assert content == b'Sample content'

    # Verify the file stream is cleared.
    assert loader.file is None

# ** test: file_loader_newline_preservation
def test_file_loader_newline_preservation(tmp_path):
    '''
    Test that the newline parameter is preserved and used correctly.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a file with specific newline characters.
    file_path = tmp_path / 'newline_test.txt'
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('Line 1\nLine 2\nLine 3\n')

    # Read back with newline parameter.
    with FileLoader(path=file_path, mode='r', encoding='utf-8', newline='\n') as f:
        lines = f.readlines()

    # Verify the lines preserve newline characters.
    assert lines == ['Line 1\n', 'Line 2\n', 'Line 3\n']

# ** test: file_loader_write_creates_new_file
def test_file_loader_write_creates_new_file(tmp_path):
    '''
    Test that write mode creates a new file if it does not exist.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Define a path to a new file.
    new_file = tmp_path / 'new_file.txt'

    # Verify the file does not exist yet.
    assert not new_file.exists()

    # Write content to the new file.
    with FileLoader(path=new_file, mode='w', encoding='utf-8') as f:
        f.write('Created content')

    # Verify the file was created and has the correct content.
    assert new_file.exists()
    assert new_file.read_text(encoding='utf-8') == 'Created content'

# ** test: file_loader_close_when_not_open
def test_file_loader_close_when_not_open(temp_text_file):
    '''
    Test that closing a file that was never opened is a no-op.

    :param temp_text_file: The path to the temporary text file.
    :type temp_text_file: pathlib.Path
    '''

    # Create a FileLoader but do not open it.
    loader = FileLoader(path=temp_text_file, mode='r', encoding='utf-8')

    # Calling close_file should not raise.
    loader.close_file()

    # Verify file is still None.
    assert loader.file is None
