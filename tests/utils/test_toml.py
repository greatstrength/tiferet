"""Tiferet TomlLoader Utility Tests"""

# *** imports

# ** infra
import pytest
from pathlib import Path

# ** app
from tiferet.utils.toml import (
    TomlLoader,
    TOML_FILE_NOT_FOUND_ID,
    TOML_FILE_LOAD_ERROR_ID,
    INVALID_TOML_FILE_ID,
)
from tiferet.utils.file import FILE_NOT_FOUND_ID
from tiferet.interfaces.core import ServiceError

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

# *** tests

# ** test: toml_loader_load_basic
def test_toml_loader_load_basic(tmp_path):
    '''
    Test loading a valid TOML file returns parsed data.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'config.toml')
    Path(file_path).write_text('[project]\nname = "tiferet"\nversion = "2.0.0"\n\n[project.options]\ndebug = true\ncount = 42\n', encoding='utf-8')
    loader = TomlLoader(path=file_path)

    # Run the case steps.
    data = loader.load()

    # Assert the case expectations.
    assert data == {'project': {'name': 'tiferet', 'version': '2.0.0', 'options': {'debug': True, 'count': 42}}}

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
def test_toml_loader_load_file_not_found(tmp_path):
    '''
    Test that loading a nonexistent TOML file raises FILE_NOT_FOUND.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('missing.toml'))
    loader = TomlLoader(path=file_path)

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.load()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID

# ** test: toml_loader_load_invalid_toml
def test_toml_loader_load_invalid_toml(tmp_path):
    '''
    Test that loading a malformed TOML file raises TOML_FILE_LOAD_ERROR.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'bad.toml')
    Path(file_path).write_text('[invalid\nkey = ???\n', encoding='utf-8')
    loader = TomlLoader(path=file_path)

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        loader.load()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == TOML_FILE_LOAD_ERROR_ID

# ** test: toml_loader_verify_toml_file_wrong_extension
def test_toml_loader_verify_toml_file_wrong_extension(tmp_path):
    '''
    Test that verify_toml_file raises INVALID_TOML_FILE for non-.toml files.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path / 'config.yaml')
    Path(file_path).write_text('key: value', encoding='utf-8')
    loader = TomlLoader(path=file_path)

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        TomlLoader.verify_toml_file(loader)
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == INVALID_TOML_FILE_ID

# ** test: toml_loader_verify_toml_file_not_found
def test_toml_loader_verify_toml_file_not_found(tmp_path):
    '''
    Test that verify_toml_file raises TOML_FILE_NOT_FOUND for missing files.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file and construct the loader.
    file_path = str(tmp_path.joinpath('missing.toml'))
    loader = TomlLoader(path=file_path)

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        TomlLoader.verify_toml_file(loader)
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == TOML_FILE_NOT_FOUND_ID

# ** test: toml_loader_defaults_to_binary_mode
def test_toml_loader_defaults_to_binary_mode():
    '''
    Test that TomlLoader defaults to binary read mode as required by tomllib.
    '''

    # Run the case steps.
    loader = TomlLoader(path='/tmp/test.toml')

    # Assert the case expectations.
    assert loader.mode == 'rb'
    assert loader.encoding is None
