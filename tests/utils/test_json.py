"""Tiferet Utils Json Tests"""

# *** imports

# ** core
import json
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.utils.file import FILE_NOT_FOUND_ID, INVALID_FILE_ID
from tiferet.utils.json import (
    JsonLoader,
    INVALID_JSON_PATH_ID,
    JSON_FILE_LOAD_ERROR_ID,
    JSON_FILE_NOT_FOUND_ID,
)

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

# *** testers

# ** tester: test_json_loader
@use_tester(
    type='generic',
    target_cls=JsonLoader,
)
class TestJsonLoader:
    '''JsonLoader binder coverage via GenericTesterContext.'''

    # * test: load_success
    def test_load_success(
            self,
            test_ctx,
            temp_json_file: Path,
            sample_json_dict: dict,
        ) -> None:
        '''
        Test successful loading and parsing of a JSON file.

        :param temp_json_file: The path to the temporary JSON file.
        :type temp_json_file: pathlib.Path
        :param sample_json_dict: The expected parsed dict.
        :type sample_json_dict: dict
        '''

        # Load the JSON file.
        loader = test_ctx.make_target(data={'path': temp_json_file, 'mode': 'r'})
        result = loader.load()

        # Verify the result matches the expected dict.
        assert result == sample_json_dict

    # * test: load_with_transformations
    def test_load_with_transformations(self, test_ctx, temp_json_file: Path) -> None:
        '''
        Test load() with start_node and data_factory transformations.

        :param temp_json_file: The path to the temporary JSON file.
        :type temp_json_file: pathlib.Path
        '''

        # Load using start_node to extract items and data_factory to get the count.
        loader = test_ctx.make_target(data={'path': temp_json_file, 'mode': 'r'})
        result = loader.load(
            start_node=lambda d: d['items'],
            data_factory=lambda items: len(items),
        )

        # Verify the transformation chain produced the expected result.
        assert result == 2

    # * test: save_and_reload
    def test_save_and_reload(self, test_ctx, tmp_path) -> None:
        '''
        Test round-trip: save data to JSON then load it back.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Define the file path and data to save.
        file_path = tmp_path / 'output.json'
        data = {'key': 'value', 'numbers': [1, 2, 3]}

        # Save the data to a JSON file.
        saver = test_ctx.make_target(data={'path': file_path, 'mode': 'w'})
        saver.save(data)

        # Reload the saved file.
        loader = test_ctx.make_target(data={'path': file_path, 'mode': 'r'})
        result = loader.load()

        # Verify round-trip produces the same data.
        assert result == data

    # * test: load_file_not_found
    def test_load_file_not_found(self, test_ctx, tmp_path) -> None:
        '''
        Test that loading a non-existent JSON file raises a structured error.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create a loader pointing to a non-existent file.
        loader = test_ctx.make_target(
            data={'path': tmp_path / 'missing.json', 'mode': 'r'},
        )

        # Attempt to load; expect FILE_NOT_FOUND error from FileLoader.
        with pytest.raises(ServiceError) as exc_info:
            loader.load()

        # Verify the error code.
        assert exc_info.value.error_code == FILE_NOT_FOUND_ID

    # * test: load_malformed_json
    def test_load_malformed_json(self, test_ctx, tmp_path) -> None:
        '''
        Test that loading malformed JSON raises JSON_FILE_LOAD_ERROR.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Write malformed JSON content.
        file_path = tmp_path / 'bad.json'
        file_path.write_text('{"key": [unclosed bracket', encoding='utf-8')

        # Attempt to load the malformed JSON.
        loader = test_ctx.make_target(data={'path': file_path, 'mode': 'r'})
        with pytest.raises(ServiceError) as exc_info:
            loader.load()

        # Verify the error code and kwargs.
        assert exc_info.value.error_code == JSON_FILE_LOAD_ERROR_ID
        assert 'path' in exc_info.value.kwargs

    # * test: save_write_failure
    def test_save_write_failure(self, test_ctx, tmp_path) -> None:
        '''
        Test that a write failure raises a structured error.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Point to a path within a non-existent parent directory.
        file_path = tmp_path / 'nonexistent_dir' / 'output.json'
        saver = test_ctx.make_target(data={'path': file_path, 'mode': 'w'})

        # Attempt to save; expect an error due to missing parent directory.
        with pytest.raises(ServiceError) as exc_info:
            saver.save({'key': 'value'})

        # Verify the error code (FILE_NOT_FOUND propagates from FileLoader).
        assert exc_info.value.error_code == FILE_NOT_FOUND_ID

    # * test: parse_json_path_dict
    def test_parse_json_path_dict(self, nested_json_data: dict) -> None:
        '''
        Test parse_json_path navigating nested dict keys.

        :param nested_json_data: The nested JSON data fixture.
        :type nested_json_data: dict
        '''

        # Navigate to a nested dict value.
        result = JsonLoader.parse_json_path(nested_json_data, 'metadata.total')

        # Verify the resolved value.
        assert result == 2

    # * test: parse_json_path_list
    def test_parse_json_path_list(self, nested_json_data: dict) -> None:
        '''
        Test parse_json_path navigating through list indices.

        :param nested_json_data: The nested JSON data fixture.
        :type nested_json_data: dict
        '''

        # Navigate to a nested list element.
        result = JsonLoader.parse_json_path(nested_json_data, 'users.1.name')

        # Verify the resolved value.
        assert result == 'Bob'

    # * test: parse_json_path_missing_key
    def test_parse_json_path_missing_key(self, nested_json_data: dict) -> None:
        '''
        Test parse_json_path returns None for a missing dict key.

        :param nested_json_data: The nested JSON data fixture.
        :type nested_json_data: dict
        '''

        # Navigate to a non-existent key.
        result = JsonLoader.parse_json_path(nested_json_data, 'metadata.missing')

        # Verify the result is None.
        assert result is None

    # * test: parse_json_path_invalid
    def test_parse_json_path_invalid(self, nested_json_data: dict) -> None:
        '''
        Test parse_json_path raises INVALID_JSON_PATH on invalid navigation.

        :param nested_json_data: The nested JSON data fixture.
        :type nested_json_data: dict
        '''

        # Attempt to navigate through a non-dict/non-list value.
        with pytest.raises(ServiceError) as exc_info:
            JsonLoader.parse_json_path(nested_json_data, 'metadata.total.invalid')

        # Verify the error code.
        assert exc_info.value.error_code == INVALID_JSON_PATH_ID

    # * test: verify_json_file_success
    def test_verify_json_file_success(self, test_ctx, temp_json_file: Path) -> None:
        '''
        Test that verify_json_file succeeds for a valid, existing JSON file.

        :param temp_json_file: The path to the temporary JSON file.
        :type temp_json_file: pathlib.Path
        '''

        # Create a loader and verify — should not raise.
        loader = test_ctx.make_target(data={'path': temp_json_file, 'mode': 'r'})
        JsonLoader.verify_json_file(loader)

    # * test: verify_json_file_invalid_extension
    def test_verify_json_file_invalid_extension(self, test_ctx, tmp_path) -> None:
        '''
        Test that verify_json_file raises INVALID_FILE for non-JSON extension.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create a file with a .txt extension.
        file_path = tmp_path / 'data.txt'
        file_path.write_text('{"key": "value"}', encoding='utf-8')

        # Verify raises INVALID_FILE error.
        loader = test_ctx.make_target(data={'path': file_path, 'mode': 'r'})
        with pytest.raises(ServiceError) as exc_info:
            JsonLoader.verify_json_file(loader)

        # Verify the error code.
        assert exc_info.value.error_code == INVALID_FILE_ID

    # * test: verify_json_file_not_found
    def test_verify_json_file_not_found(self, test_ctx, tmp_path) -> None:
        '''
        Test that verify_json_file raises JSON_FILE_NOT_FOUND for a missing JSON file.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create a loader pointing to a non-existent JSON file.
        loader = test_ctx.make_target(
            data={'path': tmp_path / 'missing.json', 'mode': 'r'},
        )

        # Verify raises JSON_FILE_NOT_FOUND error.
        with pytest.raises(ServiceError) as exc_info:
            JsonLoader.verify_json_file(loader)

        # Verify the error code and kwargs.
        assert exc_info.value.error_code == JSON_FILE_NOT_FOUND_ID
        assert 'missing.json' in exc_info.value.kwargs.get('path', '')

    # * test: verify_json_file_fallback
    def test_verify_json_file_fallback(self, test_ctx, tmp_path) -> None:
        '''
        Test that verify_json_file falls back to default_path when primary has invalid extension.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create the fallback JSON file.
        fallback_path = tmp_path / 'fallback.json'
        fallback_path.write_text('{}', encoding='utf-8')

        # Create a loader with a non-JSON extension.
        loader = test_ctx.make_target(
            data={'path': tmp_path / 'data.txt', 'mode': 'r'},
        )

        # Verify succeeds using the fallback path.
        JsonLoader.verify_json_file(loader, default_path=fallback_path)

    # * test: context_manager_closes_on_error
    def test_context_manager_closes_on_error(self, test_ctx, tmp_path) -> None:
        '''
        Test that the file stream is closed even when a parse error occurs.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Write malformed JSON content.
        file_path = tmp_path / 'broken.json'
        file_path.write_text('{invalid json', encoding='utf-8')

        # Attempt to load, which should raise.
        loader = test_ctx.make_target(data={'path': file_path, 'mode': 'r'})
        with pytest.raises(ServiceError):
            loader.load()

        # Verify the file stream is closed after the error.
        assert loader.file is None
