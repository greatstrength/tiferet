"""Tiferet Utils Yaml Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from ..yaml import YamlLoader
from ...events import a
from ...events.settings import TiferetError

# *** fixtures

# ** fixture: sample_yaml_content
@pytest.fixture
def sample_yaml_content() -> str:
    '''
    Fixture providing a sample YAML string.

    :return: A YAML-formatted string.
    :rtype: str
    '''

    # Return a sample YAML string.
    return 'name: test\nitems:\n  - one\n  - two\ncount: 3\n'

# ** fixture: sample_yaml_dict
@pytest.fixture
def sample_yaml_dict() -> dict:
    '''
    Fixture providing the expected dict from sample YAML content.

    :return: A dict matching the sample YAML content.
    :rtype: dict
    '''

    # Return the expected dict.
    return {'name': 'test', 'items': ['one', 'two'], 'count': 3}

# ** fixture: temp_yaml_file
@pytest.fixture
def temp_yaml_file(tmp_path, sample_yaml_content) -> Path:
    '''
    Fixture to create a temporary YAML file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_yaml_content: The sample YAML content string.
    :type sample_yaml_content: str
    :return: The path to the created temporary YAML file.
    :rtype: pathlib.Path
    '''

    # Create a temporary YAML file with sample content.
    file_path = tmp_path / 'test.yaml'
    file_path.write_text(sample_yaml_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: temp_yml_file
@pytest.fixture
def temp_yml_file(tmp_path, sample_yaml_content) -> Path:
    '''
    Fixture to create a temporary .yml file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_yaml_content: The sample YAML content string.
    :type sample_yaml_content: str
    :return: The path to the created temporary .yml file.
    :rtype: pathlib.Path
    '''

    # Create a temporary .yml file with sample content.
    file_path = tmp_path / 'test.yml'
    file_path.write_text(sample_yaml_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: temp_empty_yaml_file
@pytest.fixture
def temp_empty_yaml_file(tmp_path) -> Path:
    '''
    Fixture to create an empty temporary YAML file.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created empty YAML file.
    :rtype: pathlib.Path
    '''

    # Create an empty YAML file.
    file_path = tmp_path / 'empty.yaml'
    file_path.write_text('', encoding='utf-8')

    # Return the file path.
    return file_path

# *** tests

# ** test: yaml_loader_load_success
def test_yaml_loader_load_success(temp_yaml_file: Path, sample_yaml_dict: dict):
    '''
    Test successful loading and parsing of a YAML file.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: pathlib.Path
    :param sample_yaml_dict: The expected parsed dict.
    :type sample_yaml_dict: dict
    '''

    # Load the YAML file.
    loader = YamlLoader(path=temp_yaml_file, mode='r')
    result = loader.load()

    # Verify the result matches the expected dict.
    assert result == sample_yaml_dict

# ** test: yaml_loader_load_yml_extension
def test_yaml_loader_load_yml_extension(temp_yml_file: Path, sample_yaml_dict: dict):
    '''
    Test successful loading of a .yml file.

    :param temp_yml_file: The path to the temporary .yml file.
    :type temp_yml_file: pathlib.Path
    :param sample_yaml_dict: The expected parsed dict.
    :type sample_yaml_dict: dict
    '''

    # Load the .yml file.
    loader = YamlLoader(path=temp_yml_file, mode='r')
    result = loader.load()

    # Verify the result matches the expected dict.
    assert result == sample_yaml_dict

# ** test: yaml_loader_load_with_transformations
def test_yaml_loader_load_with_transformations(temp_yaml_file: Path):
    '''
    Test load() with start_node and data_factory transformations.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: pathlib.Path
    '''

    # Load using start_node to extract items and data_factory to get the count.
    loader = YamlLoader(path=temp_yaml_file, mode='r')
    result = loader.load(
        start_node=lambda d: d['items'],
        data_factory=lambda items: len(items),
    )

    # Verify the transformation chain produced the expected result.
    assert result == 2

# ** test: yaml_loader_load_empty_file
def test_yaml_loader_load_empty_file(temp_empty_yaml_file: Path):
    '''
    Test that loading an empty YAML file returns an empty dict.

    :param temp_empty_yaml_file: The path to the empty YAML file.
    :type temp_empty_yaml_file: pathlib.Path
    '''

    # Load the empty YAML file.
    loader = YamlLoader(path=temp_empty_yaml_file, mode='r')
    result = loader.load()

    # Verify empty YAML returns an empty dict.
    assert result == {}

# ** test: yaml_loader_save_and_reload
def test_yaml_loader_save_and_reload(tmp_path):
    '''
    Test round-trip: save data to YAML then load it back.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Define the file path and data to save.
    file_path = tmp_path / 'output.yaml'
    data = {'key': 'value', 'numbers': [1, 2, 3]}

    # Save the data to a YAML file.
    saver = YamlLoader(path=file_path, mode='w')
    saver.save(data)

    # Reload the saved file.
    loader = YamlLoader(path=file_path, mode='r')
    result = loader.load()

    # Verify round-trip produces the same data.
    assert result == data

# ** test: yaml_loader_load_file_not_found
def test_yaml_loader_load_file_not_found(tmp_path):
    '''
    Test that loading a non-existent YAML file raises a structured error.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a loader pointing to a non-existent file.
    loader = YamlLoader(path=tmp_path / 'missing.yaml', mode='r')

    # Attempt to load; expect FILE_NOT_FOUND error from FileLoader.
    with pytest.raises(TiferetError) as exc_info:
        loader.load()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID

# ** test: yaml_loader_load_malformed_yaml
def test_yaml_loader_load_malformed_yaml(tmp_path):
    '''
    Test that loading malformed YAML raises YAML_FILE_LOAD_ERROR.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Write malformed YAML content.
    file_path = tmp_path / 'bad.yaml'
    file_path.write_text('key: [unclosed bracket', encoding='utf-8')

    # Attempt to load the malformed YAML.
    loader = YamlLoader(path=file_path, mode='r')
    with pytest.raises(TiferetError) as exc_info:
        loader.load()

    # Verify the error code and kwargs.
    assert exc_info.value.error_code == a.const.YAML_FILE_LOAD_ERROR_ID
    assert 'path' in exc_info.value.kwargs

# ** test: yaml_loader_save_write_failure
def test_yaml_loader_save_write_failure(tmp_path):
    '''
    Test that a write failure raises YAML_FILE_SAVE_ERROR.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Point to a path within a non-existent parent directory.
    file_path = tmp_path / 'nonexistent_dir' / 'output.yaml'
    saver = YamlLoader(path=file_path, mode='w')

    # Attempt to save; expect an error due to missing parent directory.
    with pytest.raises(TiferetError) as exc_info:
        saver.save({'key': 'value'})

    # Verify the error code (FILE_NOT_FOUND propagates from FileLoader).
    assert exc_info.value.error_code == a.const.FILE_NOT_FOUND_ID

# ** test: yaml_loader_verify_yaml_file_success
def test_yaml_loader_verify_yaml_file_success(temp_yaml_file: Path):
    '''
    Test that verify_yaml_file succeeds for a valid, existing YAML file.

    :param temp_yaml_file: The path to the temporary YAML file.
    :type temp_yaml_file: pathlib.Path
    '''

    # Create a loader and verify — should not raise.
    loader = YamlLoader(path=temp_yaml_file, mode='r')
    YamlLoader.verify_yaml_file(loader)

# ** test: yaml_loader_verify_yaml_file_invalid_extension
def test_yaml_loader_verify_yaml_file_invalid_extension(tmp_path):
    '''
    Test that verify_yaml_file raises INVALID_FILE for non-YAML extension.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a file with a .txt extension.
    file_path = tmp_path / 'data.txt'
    file_path.write_text('key: value', encoding='utf-8')

    # Verify raises INVALID_FILE error.
    loader = YamlLoader(path=file_path, mode='r')
    with pytest.raises(TiferetError) as exc_info:
        YamlLoader.verify_yaml_file(loader)

    # Verify the error code.
    assert exc_info.value.error_code == a.const.INVALID_FILE_ID

# ** test: yaml_loader_verify_yaml_file_fallback
def test_yaml_loader_verify_yaml_file_fallback(tmp_path):
    '''
    Test that verify_yaml_file falls back to default_path when primary has invalid extension.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create the fallback YAML file.
    fallback_path = tmp_path / 'fallback.yaml'
    fallback_path.write_text('key: value', encoding='utf-8')

    # Create a loader with a non-YAML extension.
    loader = YamlLoader(path=tmp_path / 'data.txt', mode='r')

    # Verify succeeds using the fallback path.
    YamlLoader.verify_yaml_file(loader, default_path=fallback_path)

# ** test: yaml_loader_verify_yaml_file_not_found
def test_yaml_loader_verify_yaml_file_not_found(tmp_path):
    '''
    Test that verify_yaml_file raises YAML_FILE_NOT_FOUND for a missing YAML file.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a loader pointing to a non-existent YAML file.
    loader = YamlLoader(path=tmp_path / 'missing.yaml', mode='r')

    # Verify raises YAML_FILE_NOT_FOUND error.
    with pytest.raises(TiferetError) as exc_info:
        YamlLoader.verify_yaml_file(loader)

    # Verify the error code and kwargs.
    assert exc_info.value.error_code == a.const.YAML_FILE_NOT_FOUND_ID
    assert 'missing.yaml' in exc_info.value.kwargs.get('path', '')

# ** test: yaml_loader_context_manager_closes_on_error
def test_yaml_loader_context_manager_closes_on_error(tmp_path):
    '''
    Test that the file stream is closed even when a parse error occurs.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Write malformed YAML content.
    file_path = tmp_path / 'broken.yaml'
    file_path.write_text(': :\n  - [invalid', encoding='utf-8')

    # Attempt to load, which should raise.
    loader = YamlLoader(path=file_path, mode='r')
    with pytest.raises(TiferetError):
        loader.load()

    # Verify the file stream is closed after the error.
    assert loader.file is None
