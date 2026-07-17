"""Tiferet TomlLoader Utility Tests"""

# *** imports

# ** infra
import pytest
from pathlib import Path

# ** app
from tiferet.utils.toml import TomlLoader
from tiferet.assets.exceptions import TiferetError
from tiferet.assets.error import (
    TOML_FILE_NOT_FOUND_ID,
    TOML_FILE_LOAD_ERROR_ID,
    INVALID_TOML_FILE_ID,
)


# *** fixtures

# ** fixture: sample_toml_file
@pytest.fixture
def sample_toml_file(tmp_path) -> Path:
    '''
    Create a temporary TOML file with sample content.

    :param tmp_path: Pytest temporary directory fixture.
    :type tmp_path: Path
    :return: Path to the temporary TOML file.
    :rtype: Path
    '''

    # Write sample TOML content.
    file_path = tmp_path / 'config.toml'
    file_path.write_text(
        '[project]\nname = "tiferet"\nversion = "2.0.0"\n\n'
        '[project.options]\ndebug = true\ncount = 42\n',
        encoding='utf-8',
    )
    return file_path


# ** fixture: invalid_toml_file
@pytest.fixture
def invalid_toml_file(tmp_path) -> Path:
    '''
    Create a temporary TOML file with invalid content.

    :param tmp_path: Pytest temporary directory fixture.
    :type tmp_path: Path
    :return: Path to the invalid TOML file.
    :rtype: Path
    '''

    # Write invalid TOML content.
    file_path = tmp_path / 'bad.toml'
    file_path.write_bytes(b'[invalid\nkey = ???')
    return file_path


# *** tests

# ** test: toml_loader_load_basic
def test_toml_loader_load_basic(sample_toml_file: Path):
    '''
    Test loading a valid TOML file returns parsed data.

    :param sample_toml_file: Path to the sample TOML file.
    :type sample_toml_file: Path
    '''

    # Load the TOML file.
    loader = TomlLoader(path=sample_toml_file)
    data = loader.load()

    # Assert parsed structure.
    assert data['project']['name'] == 'tiferet'
    assert data['project']['version'] == '2.0.0'
    assert data['project']['options']['debug'] is True
    assert data['project']['options']['count'] == 42


# ** test: toml_loader_load_with_start_node
def test_toml_loader_load_with_start_node(sample_toml_file: Path):
    '''
    Test loading with a start_node transformation.

    :param sample_toml_file: Path to the sample TOML file.
    :type sample_toml_file: Path
    '''

    # Load with a start_node that navigates to the project section.
    loader = TomlLoader(path=sample_toml_file)
    data = loader.load(start_node=lambda d: d.get('project'))

    # Assert the start_node transformation was applied.
    assert data['name'] == 'tiferet'
    assert data['version'] == '2.0.0'


# ** test: toml_loader_load_with_data_factory
def test_toml_loader_load_with_data_factory(sample_toml_file: Path):
    '''
    Test loading with a data_factory transformation.

    :param sample_toml_file: Path to the sample TOML file.
    :type sample_toml_file: Path
    '''

    # Load with a data_factory that extracts a single value.
    loader = TomlLoader(path=sample_toml_file)
    result = loader.load(
        start_node=lambda d: d.get('project'),
        data_factory=lambda d: d.get('name'),
    )

    # Assert the factory result.
    assert result == 'tiferet'


# ** test: toml_loader_load_file_not_found
def test_toml_loader_load_file_not_found(tmp_path: Path):
    '''
    Test that loading a nonexistent TOML file raises FILE_NOT_FOUND.

    :param tmp_path: Pytest temporary directory fixture.
    :type tmp_path: Path
    '''

    # Attempt to load a nonexistent file.
    loader = TomlLoader(path=tmp_path / 'missing.toml')
    with pytest.raises(TiferetError) as exc_info:
        loader.load()

    # Assert the correct error code.
    assert exc_info.value.error_code == 'FILE_NOT_FOUND'


# ** test: toml_loader_load_invalid_toml
def test_toml_loader_load_invalid_toml(invalid_toml_file: Path):
    '''
    Test that loading a malformed TOML file raises TOML_FILE_LOAD_ERROR.

    :param invalid_toml_file: Path to the invalid TOML file.
    :type invalid_toml_file: Path
    '''

    # Attempt to load the invalid file.
    loader = TomlLoader(path=invalid_toml_file)
    with pytest.raises(TiferetError) as exc_info:
        loader.load()

    # Assert the correct error code.
    assert exc_info.value.error_code == TOML_FILE_LOAD_ERROR_ID


# ** test: toml_loader_verify_toml_file_wrong_extension
def test_toml_loader_verify_toml_file_wrong_extension(tmp_path: Path):
    '''
    Test that verify_toml_file raises INVALID_TOML_FILE for non-.toml files.

    :param tmp_path: Pytest temporary directory fixture.
    :type tmp_path: Path
    '''

    # Create a file with the wrong extension.
    file_path = tmp_path / 'config.yaml'
    file_path.write_text('key: value', encoding='utf-8')

    # Create a loader and verify.
    loader = TomlLoader(path=file_path)
    with pytest.raises(TiferetError) as exc_info:
        TomlLoader.verify_toml_file(loader)

    # Assert the correct error code.
    assert exc_info.value.error_code == INVALID_TOML_FILE_ID


# ** test: toml_loader_verify_toml_file_not_found
def test_toml_loader_verify_toml_file_not_found(tmp_path: Path):
    '''
    Test that verify_toml_file raises TOML_FILE_NOT_FOUND for missing files.

    :param tmp_path: Pytest temporary directory fixture.
    :type tmp_path: Path
    '''

    # Create a loader pointing to a non-existent .toml file.
    loader = TomlLoader(path=tmp_path / 'missing.toml')
    with pytest.raises(TiferetError) as exc_info:
        TomlLoader.verify_toml_file(loader)

    # Assert the correct error code.
    assert exc_info.value.error_code == TOML_FILE_NOT_FOUND_ID


# ** test: toml_loader_defaults_to_binary_mode
def test_toml_loader_defaults_to_binary_mode():
    '''
    Test that TomlLoader defaults to binary read mode as required by tomllib.
    '''

    # Create a loader (file need not exist for attribute checks).
    loader = TomlLoader(path='/tmp/test.toml')

    # Assert binary read mode and no encoding.
    assert loader.mode == 'rb'
    assert loader.encoding is None
