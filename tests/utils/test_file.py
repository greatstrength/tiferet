"""Tiferet Utils File Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.utils.file import (
    FileLoader,
    FILE_ALREADY_OPEN_ID,
    FILE_NOT_FOUND_ID,
    INVALID_ENCODING_ID,
    INVALID_FILE_MODE_ID,
)
from tiferet.interfaces.core import ServiceError

# *** tests

# ** test: file_loader_open_read_close_cycle
def test_file_loader_open_read_close_cycle(tmp_path):
    '''
    Test successful open, read, and close cycle.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    stream = loader.open_file()
    content = stream.read()
    loader.close_file()

    # Assert the case expectations.
    assert content == 'Sample content'
    assert loader.file is None

# ** test: file_loader_context_manager_read
def test_file_loader_context_manager_read(tmp_path):
    '''
    Test context manager usage for reading a file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    stream = loader.__enter__()
    content = stream.read()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert content == 'Sample content'
    assert loader.file is None

# ** test: file_loader_context_manager_write
def test_file_loader_context_manager_write(tmp_path):
    '''
    Test context manager usage for writing to a file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    writer = FileLoader(path=file_path, mode='w', encoding='utf-8')

    # Run the case steps.
    write_stream = writer.__enter__()
    write_stream.write('New content')
    writer.__exit__(None, None, None)
    reader = FileLoader(path=file_path, mode='r', encoding='utf-8')
    read_stream = reader.__enter__()
    content = read_stream.read()
    reader.__exit__(None, None, None)

    # Assert the case expectations.
    assert content == 'New content'

# ** test: file_loader_invalid_mode
def test_file_loader_invalid_mode(tmp_path):
    '''
    Test that an invalid file mode raises INVALID_FILE_MODE error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='z', encoding='utf-8')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.open_file()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == INVALID_FILE_MODE_ID
    assert failed.kwargs['mode'] == 'z'

# ** test: file_loader_missing_encoding_text_mode
def test_file_loader_missing_encoding_text_mode(tmp_path):
    '''
    Test that missing encoding in text mode raises INVALID_ENCODING error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding=None)

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.open_file()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == INVALID_ENCODING_ID

# ** test: file_loader_already_open
def test_file_loader_already_open(tmp_path):
    '''
    Test that opening an already-open file raises FILE_ALREADY_OPEN error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    stream = loader.__enter__()
    with pytest.raises(ServiceError) as exc_info:
        loader.open_file()
    failed = exc_info.value
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert failed.error_code == FILE_ALREADY_OPEN_ID
    assert failed.kwargs['path'] == file_path

# ** test: file_loader_file_not_found_read
def test_file_loader_file_not_found_read(tmp_path):
    '''
    Test that reading a non-existent file raises FILE_NOT_FOUND error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('does_not_exist.txt'))
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.open_file()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID
    assert failed.kwargs['path'] == file_path

# ** test: file_loader_missing_parent_dir_write
def test_file_loader_missing_parent_dir_write(tmp_path):
    '''
    Test that writing to a file with a non-existent parent directory raises FILE_NOT_FOUND error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('nonexistent_dir', 'file.txt'))
    loader = FileLoader(path=file_path, mode='w', encoding='utf-8')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.open_file()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID

# ** test: file_loader_binary_mode_no_encoding
def test_file_loader_binary_mode_no_encoding(tmp_path):
    '''
    Test that binary mode does not require encoding.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='rb', encoding=None)

    # Run the case steps.
    stream = loader.__enter__()
    content = stream.read()
    decoded = content.decode()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert isinstance(content, bytes)
    assert decoded == 'Sample content'
    assert loader.file is None

# ** test: file_loader_newline_preservation
def test_file_loader_newline_preservation(tmp_path):
    '''
    Test that the newline parameter is preserved and used correctly.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'newline_test.txt')
    Path(file_path).write_text('Line 1\nLine 2\nLine 3\n', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8', newline='\n')

    # Run the case steps.
    stream = loader.__enter__()
    lines = stream.readlines()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert lines == ['Line 1\n', 'Line 2\n', 'Line 3\n']

# ** test: file_loader_write_creates_new_file
def test_file_loader_write_creates_new_file(tmp_path):
    '''
    Test that write mode creates a new file if it does not exist.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('new_file.txt'))
    before = (tmp_path / 'new_file.txt').exists()
    writer = FileLoader(path=file_path, mode='w', encoding='utf-8')

    # Run the case steps.
    stream = writer.__enter__()
    stream.write('Created content')
    writer.__exit__(None, None, None)
    after = (tmp_path / 'new_file.txt').exists()
    content = (tmp_path / 'new_file.txt').read_text(encoding='utf-8')

    # Assert the case expectations.
    assert before is False
    assert after is True
    assert content == 'Created content'

# ** test: file_loader_close_when_not_open
def test_file_loader_close_when_not_open(tmp_path):
    '''
    Test that closing a file that was never opened is a no-op.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.txt')
    Path(file_path).write_text('Sample content', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    loader.close_file()

    # Assert the case expectations.
    assert loader.file is None

# ** test: file_loader_verify_extension_success
def test_file_loader_verify_extension_success(tmp_path):
    '''
    Test that verify_extension succeeds for an allowed, existing extension.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'config.yaml')
    Path(file_path).write_text('key: value', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    verified = FileLoader.verify_extension(
        loader=loader,
        allowed_extensions=['.yaml', '.yml'],
        invalid_error_id='INVALID_TEST_EXT',
        invalid_message='Invalid extension.',
        not_found_error_id='TEST_NOT_FOUND',
        format_name='TEST',
    )

    # Assert the case expectations.
    assert verified is None

# ** test: file_loader_verify_extension_invalid_no_fallback
def test_file_loader_verify_extension_invalid_no_fallback(tmp_path):
    '''
    Test that verify_extension raises the passed invalid_error_id and
    invalid_message when the extension is not allowed and no fallback resolves.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'config.txt')
    Path(file_path).write_text('key: value', encoding='utf-8')
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        FileLoader.verify_extension(
            loader=loader,
            allowed_extensions=['.yaml', '.yml'],
            invalid_error_id='INVALID_TEST_EXT',
            invalid_message='Invalid extension.',
            not_found_error_id='TEST_NOT_FOUND',
            format_name='TEST',
        )
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == 'INVALID_TEST_EXT'
    assert failed.message == 'Invalid extension.'

# ** test: file_loader_verify_extension_invalid_with_valid_fallback
def test_file_loader_verify_extension_invalid_with_valid_fallback(tmp_path):
    '''
    Test that verify_extension falls back to default_path when the primary
    path has an invalid extension but the fallback path is allowed.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'config.txt')
    Path(file_path).write_text('key: value', encoding='utf-8')
    default_file_path = str(tmp_path / 'default.yaml')
    Path(default_file_path).write_text('key: value', encoding='utf-8')
    default_path = Path(default_file_path)
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    verified = FileLoader.verify_extension(
        loader=loader,
        allowed_extensions=['.yaml', '.yml'],
        invalid_error_id='INVALID_TEST_EXT',
        invalid_message='Invalid extension.',
        not_found_error_id='TEST_NOT_FOUND',
        format_name='TEST',
        default_path=default_path,
    )

    # Assert the case expectations.
    assert verified is None

# ** test: file_loader_verify_extension_not_found
def test_file_loader_verify_extension_not_found(tmp_path):
    '''
    Test that verify_extension raises the passed not_found_error_id with the
    resolved path in kwargs when the file does not exist.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('missing.yaml'))
    loader = FileLoader(path=file_path, mode='r', encoding='utf-8')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        FileLoader.verify_extension(
            loader=loader,
            allowed_extensions=['.yaml', '.yml'],
            invalid_error_id='INVALID_TEST_EXT',
            invalid_message='Invalid extension.',
            not_found_error_id='TEST_NOT_FOUND',
            format_name='TEST',
        )
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == 'TEST_NOT_FOUND'
    assert failed.kwargs['path'] == file_path
