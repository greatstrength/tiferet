"""Tiferet Utils Json Tests"""

# *** imports

# ** core
import json
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.utils.json import (
    JsonLoader,
    JSON_FILE_NOT_FOUND_ID,
    JSON_FILE_LOAD_ERROR_ID,
    INVALID_JSON_PATH_ID,
)
from tiferet.utils.file import FILE_NOT_FOUND_ID, INVALID_FILE_ID
from tiferet.interfaces.core import ServiceError

# *** fixtures

# ** fixture: sample_json_dict
@pytest.fixture
def sample_json_dict() -> dict:
    '''
    Fixture providing a sample JSON-compatible dict.

    :return: A sample dict.
    :rtype: dict
    '''

    # Return a sample dict.
    return {'name': 'test', 'items': ['one', 'two'], 'count': 3}

# ** fixture: sample_json_content
@pytest.fixture
def sample_json_content(sample_json_dict) -> str:
    '''
    Fixture providing a sample JSON string.

    :param sample_json_dict: The sample dict to serialize.
    :type sample_json_dict: dict
    :return: A JSON-formatted string.
    :rtype: str
    '''

    # Return the sample dict as a JSON string.
    return json.dumps(sample_json_dict, indent=2, ensure_ascii=False) + '\n'

# ** fixture: temp_json_file
@pytest.fixture
def temp_json_file(tmp_path, sample_json_content) -> Path:
    '''
    Fixture to create a temporary JSON file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_json_content: The sample JSON content string.
    :type sample_json_content: str
    :return: The path to the created temporary JSON file.
    :rtype: pathlib.Path
    '''

    # Create a temporary JSON file with sample content.
    file_path = tmp_path / 'test.json'
    file_path.write_text(sample_json_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: nested_json_data
@pytest.fixture
def nested_json_data() -> dict:
    '''
    Fixture providing nested JSON-compatible data for path parsing tests.

    :return: A nested dict with lists.
    :rtype: dict
    '''

    # Return a nested structure.
    return {
        'users': [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
        ],
        'metadata': {
            'total': 2,
            'source': 'test',
        },
    }

# ** fixture: temp_nested_json_file
@pytest.fixture
def temp_nested_json_file(tmp_path, nested_json_data) -> Path:
    '''
    Fixture to create a temporary JSON file with nested content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param nested_json_data: The nested JSON data.
    :type nested_json_data: dict
    :return: The path to the created temporary JSON file.
    :rtype: pathlib.Path
    '''

    # Create a temporary JSON file with nested content.
    file_path = tmp_path / 'nested.json'
    file_path.write_text(
        json.dumps(nested_json_data, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )

    # Return the file path.
    return file_path

# *** tests

# ** test: json_loader_load_success
def test_json_loader_load_success(tmp_path):
    '''
    Test successful loading and parsing of a JSON file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.json')
    Path(file_path).write_text('{\n  "name": "test",\n  "items": [\n    "one",\n    "two"\n  ],\n  "count": 3\n}\n', encoding='utf-8')
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    result = loader.load()

    # Assert the case expectations.
    assert result == {'name': 'test', 'items': ['one', 'two'], 'count': 3}

# ** test: json_loader_load_with_transformations
def test_json_loader_load_with_transformations(temp_json_file: Path):
    '''
    Test load() with start_node and data_factory transformations.

    :param temp_json_file: The path to the temporary JSON file.
    :type temp_json_file: pathlib.Path
    '''

    # Load using start_node to extract items and data_factory to get the count.
    loader = JsonLoader(path=temp_json_file, mode='r')
    result = loader.load(
        start_node=lambda d: d['items'],
        data_factory=lambda items: len(items),
    )

    # Verify the transformation chain produced the expected result.
    assert result == 2

# ** test: json_loader_save_and_reload
def test_json_loader_save_and_reload(tmp_path):
    '''
    Test round-trip: save data to JSON then load it back.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('output.json'))
    saver = JsonLoader(path=file_path, mode='w')

    # Run the case steps.
    saver.save({'key': 'value', 'numbers': [1, 2, 3]})
    loader = JsonLoader(path=file_path, mode='r')
    result = loader.load()

    # Assert the case expectations.
    assert result == {'key': 'value', 'numbers': [1, 2, 3]}

# ** test: json_loader_load_file_not_found
def test_json_loader_load_file_not_found(tmp_path):
    '''
    Test that loading a non-existent JSON file raises a structured error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('missing.json'))
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.load()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID

# ** test: json_loader_load_malformed_json
def test_json_loader_load_malformed_json(tmp_path):
    '''
    Test that loading malformed JSON raises JSON_FILE_LOAD_ERROR.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'bad.json')
    Path(file_path).write_text('{"key": [unclosed bracket', encoding='utf-8')
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.load()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == JSON_FILE_LOAD_ERROR_ID
    assert failed.kwargs['path'] == file_path

# ** test: json_loader_save_write_failure
def test_json_loader_save_write_failure(tmp_path):
    '''
    Test that a write failure raises a structured error.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('nonexistent_dir', 'output.json'))
    saver = JsonLoader(path=file_path, mode='w')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        saver.save({'key': 'value'})
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID

# ** test: json_loader_parse_json_path_dict
def test_json_loader_parse_json_path_dict():
    '''
    Test parse_json_path navigating nested dict keys.
    '''

    # Run the case steps.
    result = JsonLoader.parse_json_path({'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], 'metadata': {'total': 2, 'source': 'test'}}, 'metadata.total')

    # Assert the case expectations.
    assert result == 2

# ** test: json_loader_parse_json_path_list
def test_json_loader_parse_json_path_list():
    '''
    Test parse_json_path navigating through list indices.
    '''

    # Run the case steps.
    result = JsonLoader.parse_json_path({'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], 'metadata': {'total': 2, 'source': 'test'}}, 'users.1.name')

    # Assert the case expectations.
    assert result == 'Bob'

# ** test: json_loader_parse_json_path_missing_key
def test_json_loader_parse_json_path_missing_key():
    '''
    Test parse_json_path returns None for a missing dict key.
    '''

    # Run the case steps.
    result = JsonLoader.parse_json_path({'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], 'metadata': {'total': 2, 'source': 'test'}}, 'metadata.missing')

    # Assert the case expectations.
    assert result is None

# ** test: json_loader_parse_json_path_invalid
def test_json_loader_parse_json_path_invalid():
    '''
    Test parse_json_path raises INVALID_JSON_PATH on invalid navigation.
    '''

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        JsonLoader.parse_json_path({'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], 'metadata': {'total': 2, 'source': 'test'}}, 'metadata.total.invalid')
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == INVALID_JSON_PATH_ID

# ** test: json_loader_verify_json_file_success
def test_json_loader_verify_json_file_success(tmp_path):
    '''
    Test that verify_json_file succeeds for a valid, existing JSON file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'test.json')
    Path(file_path).write_text('{\n  "name": "test",\n  "items": [\n    "one",\n    "two"\n  ],\n  "count": 3\n}\n', encoding='utf-8')
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    verified = JsonLoader.verify_json_file(loader)

    # Assert the case expectations.
    assert verified is None

# ** test: json_loader_verify_json_file_invalid_extension
def test_json_loader_verify_json_file_invalid_extension(tmp_path):
    '''
    Test that verify_json_file raises INVALID_FILE for non-JSON extension.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'data.txt')
    Path(file_path).write_text('{"key": "value"}', encoding='utf-8')
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        JsonLoader.verify_json_file(loader)
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == INVALID_FILE_ID

# ** test: json_loader_verify_json_file_not_found
def test_json_loader_verify_json_file_not_found(tmp_path):
    '''
    Test that verify_json_file raises JSON_FILE_NOT_FOUND for a missing JSON file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('missing.json'))
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        JsonLoader.verify_json_file(loader)
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == JSON_FILE_NOT_FOUND_ID
    assert failed.kwargs['path'] == file_path

# ** test: json_loader_verify_json_file_fallback
def test_json_loader_verify_json_file_fallback(tmp_path):
    '''
    Test that verify_json_file falls back to default_path when primary has invalid extension.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('data.txt'))
    fallback_file_path = str(tmp_path / 'fallback.json')
    Path(fallback_file_path).write_text('{}', encoding='utf-8')
    default_path = Path(fallback_file_path)
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    verified = JsonLoader.verify_json_file(loader, default_path=default_path)

    # Assert the case expectations.
    assert verified is None

# ** test: json_loader_context_manager_closes_on_error
def test_json_loader_context_manager_closes_on_error(tmp_path):
    '''
    Test that the file stream is closed even when a parse error occurs.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'broken.json')
    Path(file_path).write_text('{invalid json', encoding='utf-8')
    loader = JsonLoader(path=file_path, mode='r')

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.load()
    failed = exc_info.value

    # Assert the case expectations.
    assert isinstance(failed, ServiceError)
    assert loader.file is None
