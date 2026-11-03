"""Tiferet Utils Csv Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.utils.csv import (
    CsvLoader,
    CsvDictLoader,
    CSV_FIELDNAMES_REQUIRED_ID,
    CSV_INVALID_READ_MODE_ID,
    CSV_INVALID_WRITE_MODE_ID,
)
from tiferet.utils.file import FILE_NOT_FOUND_ID
from tiferet.interfaces.core import ServiceError

# *** fixtures

# ** fixture: sample_dict_csv_content
@pytest.fixture
def sample_dict_csv_content() -> str:
    '''
    Fixture providing sample CSV content with a header for dict-based reading.

    :return: A CSV-formatted string with a header row.
    :rtype: str
    '''

    # Return sample CSV content with header.
    return 'name,age,city\nAlice,30,New York\nBob,25,London\n'

# ** fixture: temp_dict_csv_file
@pytest.fixture
def temp_dict_csv_file(tmp_path, sample_dict_csv_content) -> Path:
    '''
    Fixture to create a temporary CSV file for dict-based reading.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_dict_csv_content: The sample CSV content with header.
    :type sample_dict_csv_content: str
    :return: The path to the created temporary CSV file.
    :rtype: pathlib.Path
    '''

    # Create a temporary CSV file with header content.
    file_path = tmp_path / 'dict_test.csv'
    file_path.write_text(sample_dict_csv_content, encoding='utf-8')

    # Return the file path.
    return file_path

# *** tests

# ** test: csv_loader_read_all
def test_csv_loader_read_all(tmp_path):
    '''
    Test reading all rows from a CSV file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    result = loader.read_all()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [['name', 'age', 'city'], ['Alice', '30', 'New York'], ['Bob', '25', 'London'], ['Charlie', '35', 'Paris']]

# ** test: csv_loader_read_row
def test_csv_loader_read_row(tmp_path):
    '''
    Test reading rows one at a time from a CSV file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    first = loader.read_row()
    second = loader.read_row()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert first == ['name', 'age', 'city']
    assert second == ['Alice', '30', 'New York']

# ** test: csv_loader_read_row_eof
def test_csv_loader_read_row_eof(tmp_path):
    '''
    Test that reading past EOF returns an empty list.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'empty.csv')
    Path(file_path).write_text('', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    result = loader.read_row()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == []

# ** test: csv_loader_write_row
def test_csv_loader_write_row(tmp_path):
    '''
    Test writing a single row to a CSV file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name the output CSV on the stage and construct the writer.
    file_path = str(tmp_path.joinpath('output.csv'))
    writer = CsvLoader(path=file_path, mode='w')

    # Run the case steps.
    writer.__enter__()
    writer.write_row(['name', 'age'])
    writer.__exit__(None, None, None)
    reader = CsvLoader(path=file_path, mode='r')
    reader.__enter__()
    rows = reader.read_all()
    reader.__exit__(None, None, None)

    # Assert the case expectations.
    assert rows == [['name', 'age']]

# ** test: csv_loader_write_all
def test_csv_loader_write_all(tmp_path):
    '''
    Test writing multiple rows to a CSV file.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name the output CSV on the stage and construct the writer.
    file_path = str(tmp_path.joinpath('output.csv'))
    writer = CsvLoader(path=file_path, mode='w')

    # Run the case steps.
    writer.__enter__()
    writer.write_all([['a', 'b'], ['1', '2'], ['3', '4']])
    writer.__exit__(None, None, None)
    reader = CsvLoader(path=file_path, mode='r')
    reader.__enter__()
    result = reader.read_all()
    reader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [['a', 'b'], ['1', '2'], ['3', '4']]

# ** test: csv_loader_save_and_reload
def test_csv_loader_save_and_reload(tmp_path):
    '''
    Test round-trip: write rows then read them back.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('roundtrip.csv'))

    # Run the case steps.
    CsvLoader.save_rows(file_path, [['x', 'y'], ['10', '20'], ['30', '40']])
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['x', 'y'], ['10', '20'], ['30', '40']]

# ** test: csv_loader_load_rows_static
def test_csv_loader_load_rows_static(tmp_path):
    '''
    Test the static load_rows helper.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')

    # Run the case steps.
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['name', 'age', 'city'], ['Alice', '30', 'New York'], ['Bob', '25', 'London'], ['Charlie', '35', 'Paris']]

# ** test: csv_loader_save_rows_static_list
def test_csv_loader_save_rows_static_list(tmp_path):
    '''
    Test the static save_rows helper with list-based rows.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('list_output.csv'))

    # Run the case steps.
    CsvLoader.save_rows(file_path, [['col1', 'col2'], ['a', 'b']])
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['col1', 'col2'], ['a', 'b']]

# ** test: csv_loader_save_rows_dict_mode
def test_csv_loader_save_rows_dict_mode(tmp_path):
    '''
    Test the static save_rows helper with dict-based rows.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('dict_output.csv'))

    # Run the case steps.
    CsvLoader.save_rows(
        file_path,
        [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}],
        fieldnames=['name', 'age'],
    )
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['name', 'age'], ['Alice', '30'], ['Bob', '25']]

# ** test: csv_loader_save_rows_dict_no_fieldnames
def test_csv_loader_save_rows_dict_no_fieldnames(tmp_path):
    '''
    Test that save_rows raises CSV_FIELDNAMES_REQUIRED when writing dicts without fieldnames.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('dict_no_fields.csv'))

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        CsvLoader.save_rows(file_path, [{'name': 'Alice'}])
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == CSV_FIELDNAMES_REQUIRED_ID
    assert failed.message == 'Fieldnames must be provided when writing dict-based CSV rows.'
    assert failed.kwargs['path'] == file_path
    assert failed.class_name == 'CsvLoader'

# ** test: csv_loader_append_row_static
def test_csv_loader_append_row_static(tmp_path):
    '''
    Test the static append_row helper.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('append.csv'))

    # Run the case steps.
    CsvLoader.save_rows(file_path, [['header1', 'header2'], ['a', 'b']])
    CsvLoader.append_row(file_path, ['c', 'd'])
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['header1', 'header2'], ['a', 'b'], ['c', 'd']]

# ** test: csv_loader_yield_rows
def test_csv_loader_yield_rows(tmp_path):
    '''
    Test yield_rows returns all rows as a generator.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    generator = loader.yield_rows()
    result = list(generator)
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [['name', 'age', 'city'], ['Alice', '30', 'New York'], ['Bob', '25', 'London'], ['Charlie', '35', 'Paris']]

# ** test: csv_loader_yield_rows_with_range
def test_csv_loader_yield_rows_with_range(tmp_path):
    '''
    Test yield_rows with start_line and end_line filtering.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    generator = loader.yield_rows(start_line=2, end_line=3)
    result = list(generator)
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [['Alice', '30', 'New York'], ['Bob', '25', 'London']]

# ** test: csv_loader_invalid_read_mode
def test_csv_loader_invalid_read_mode(tmp_path):
    '''
    Test that building a reader in write-only mode raises CSV_INVALID_READ_MODE.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name the output CSV on the stage and construct the writer.
    file_path = str(tmp_path.joinpath('write_only.csv'))
    loader = CsvLoader(path=file_path, mode='w')

    # Run the case steps.
    loader.__enter__()
    with pytest.raises(ServiceError) as exc_info:
        loader.build_reader()
    failed = exc_info.value
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert failed.error_code == CSV_INVALID_READ_MODE_ID
    assert failed.message == 'File not opened in readable mode for CSV reading.'
    assert failed.kwargs['mode'] == 'w'

# ** test: csv_loader_invalid_write_mode
def test_csv_loader_invalid_write_mode(tmp_path):
    '''
    Test that building a writer in read-only mode raises CSV_INVALID_WRITE_MODE.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    with pytest.raises(ServiceError) as exc_info:
        loader.build_writer()
    failed = exc_info.value
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert failed.error_code == CSV_INVALID_WRITE_MODE_ID
    assert failed.message == 'File not opened in writable mode for CSV writing.'
    assert failed.kwargs['mode'] == 'r'

# ** test: csv_loader_file_not_found
def test_csv_loader_file_not_found(tmp_path):
    '''
    Test that opening a non-existent CSV file raises FILE_NOT_FOUND.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name a missing CSV on the stage and construct the loader.
    file_path = str(tmp_path.joinpath('missing.csv'))
    loader = CsvLoader(path=file_path, mode='r')

    # Enter the loader.
    with pytest.raises(ServiceError) as exc_info:
        loader.__enter__()
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == FILE_NOT_FOUND_ID

# ** test: csv_loader_empty_file
def test_csv_loader_empty_file(tmp_path):
    '''
    Test that reading an empty CSV file returns an empty list.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'empty.csv')
    Path(file_path).write_text('', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    result = loader.read_all()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == []

# ** test: csv_loader_context_manager_resets_state
def test_csv_loader_context_manager_resets_state(tmp_path):
    '''
    Test that __exit__ resets reader, writer, and file to None.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n', encoding='utf-8')
    loader = CsvLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    loader.read_all()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert loader.reader is None
    assert loader.writer is None
    assert loader.file is None

# ** test: csv_dict_loader_read_all
def test_csv_dict_loader_read_all(tmp_path):
    '''
    Test reading all rows as dicts using CsvDictLoader.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the dict CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'dict_test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\n', encoding='utf-8')
    loader = CsvDictLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    result = loader.read_all()
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [{'name': 'Alice', 'age': '30', 'city': 'New York'}, {'name': 'Bob', 'age': '25', 'city': 'London'}]

# ** test: csv_dict_loader_read_row
def test_csv_dict_loader_read_row(tmp_path):
    '''
    Test reading rows one at a time as dicts.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the dict CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'dict_test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\n', encoding='utf-8')
    loader = CsvDictLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    first = loader.read_row()
    second = loader.read_row()
    eof = loader.read_row()
    loader.__exit__(None, None, None)
    eof_length = len(eof)

    # Assert the case expectations.
    assert first == {'name': 'Alice', 'age': '30', 'city': 'New York'}
    assert second == {'name': 'Bob', 'age': '25', 'city': 'London'}
    assert eof_length == 0
    assert isinstance(eof, dict)

# ** test: csv_dict_loader_write_and_reload
def test_csv_dict_loader_write_and_reload(tmp_path):
    '''
    Test round-trip: write dict rows with header then read them back.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name the output CSV on the stage and construct the writer.
    file_path = str(tmp_path.joinpath('dict_roundtrip.csv'))
    writer = CsvDictLoader(path=file_path, mode='w', fieldnames=['name', 'score'])

    # Run the case steps.
    writer.__enter__()
    writer.write_header()
    writer.write_all([{'name': 'X', 'score': '100'}, {'name': 'Y', 'score': '200'}])
    writer.__exit__(None, None, None)
    reader = CsvDictLoader(path=file_path, mode='r')
    reader.__enter__()
    result = reader.read_all()
    reader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [{'name': 'X', 'score': '100'}, {'name': 'Y', 'score': '200'}]

# ** test: csv_dict_loader_load_rows_static
def test_csv_dict_loader_load_rows_static(tmp_path):
    '''
    Test the static load_rows helper on CsvDictLoader.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path / 'dict_test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\n', encoding='utf-8')

    # Run the case steps.
    result = CsvDictLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [{'name': 'Alice', 'age': '30', 'city': 'New York'}, {'name': 'Bob', 'age': '25', 'city': 'London'}]

# ** test: csv_dict_loader_save_rows_static
def test_csv_dict_loader_save_rows_static(tmp_path):
    '''
    Test the static save_rows helper on CsvDictLoader.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('dict_save.csv'))

    # Run the case steps.
    CsvDictLoader.save_rows(file_path, [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}], fieldnames=['a', 'b'])
    result = CsvDictLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]

# ** test: csv_dict_loader_save_rows_no_fieldnames
def test_csv_dict_loader_save_rows_no_fieldnames(tmp_path):
    '''
    Test that CsvDictLoader.save_rows raises CSV_FIELDNAMES_REQUIRED without fieldnames.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('no_fields.csv'))

    # Run the case steps.
    with pytest.raises(ServiceError) as exc_info:
        CsvDictLoader.save_rows(file_path, [{'a': '1'}])
    failed = exc_info.value

    # Assert the case expectations.
    assert failed.error_code == CSV_FIELDNAMES_REQUIRED_ID
    assert failed.message == 'Fieldnames must be provided when writing dict-based CSV rows.'
    assert failed.kwargs['path'] == file_path
    assert failed.class_name == 'CsvDictLoader'

# ** test: csv_dict_loader_fieldnames_required_on_build_writer
def test_csv_dict_loader_fieldnames_required_on_build_writer(tmp_path):
    '''
    Test that building a DictWriter without fieldnames raises CSV_FIELDNAMES_REQUIRED.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Name the output CSV on the stage and construct the loader.
    file_path = str(tmp_path.joinpath('no_fieldnames.csv'))
    loader = CsvDictLoader(path=file_path, mode='w')

    # Run the case steps.
    loader.__enter__()
    with pytest.raises(ServiceError) as exc_info:
        loader.build_writer()
    failed = exc_info.value
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert failed.error_code == CSV_FIELDNAMES_REQUIRED_ID
    assert failed.message == 'Fieldnames must be provided when writing dict-based CSV rows.'
    assert failed.kwargs['path'] == file_path

# ** test: csv_dict_loader_invalid_read_mode
def test_csv_dict_loader_invalid_read_mode(tmp_path):
    '''
    Test that building a DictReader in write-only mode raises CSV_INVALID_READ_MODE.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Open in write mode and attempt to build a reader.
    file_path = tmp_path / 'dict_write_only.csv'
    with CsvDictLoader(path=file_path, mode='w', fieldnames=['name']) as loader:
        with pytest.raises(ServiceError) as exc_info:
            loader.build_reader()

    # Verify the error code, message, and mode.
    assert exc_info.value.error_code == CSV_INVALID_READ_MODE_ID
    assert exc_info.value.message == 'File not opened in readable mode for CSV reading.'
    assert exc_info.value.kwargs['mode'] == 'w'

# ** test: csv_dict_loader_invalid_write_mode
def test_csv_dict_loader_invalid_write_mode(temp_dict_csv_file: Path):
    '''
    Test that building a DictWriter in read-only mode raises CSV_INVALID_WRITE_MODE.

    :param temp_dict_csv_file: The path to the temporary CSV file with header.
    :type temp_dict_csv_file: pathlib.Path
    '''

    # Open in read mode and attempt to build a writer.
    with CsvDictLoader(path=temp_dict_csv_file, mode='r') as loader:
        with pytest.raises(ServiceError) as exc_info:
            loader.build_writer()

    # Verify the error code, message, and mode.
    assert exc_info.value.error_code == CSV_INVALID_WRITE_MODE_ID
    assert exc_info.value.message == 'File not opened in writable mode for CSV writing.'
    assert exc_info.value.kwargs['mode'] == 'r'

# ** test: csv_dict_loader_yield_rows
def test_csv_dict_loader_yield_rows(tmp_path):
    '''
    Test yield_rows returns dict rows as a generator.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the dict CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'dict_test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\n', encoding='utf-8')
    loader = CsvDictLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    generator = loader.yield_rows()
    result = list(generator)
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [{'name': 'Alice', 'age': '30', 'city': 'New York'}, {'name': 'Bob', 'age': '25', 'city': 'London'}]

# ** test: csv_dict_loader_yield_rows_with_range
def test_csv_dict_loader_yield_rows_with_range(tmp_path):
    '''
    Test yield_rows with range filtering on dict rows.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Write the dict CSV on the stage and construct the loader.
    file_path = str(tmp_path / 'dict_test.csv')
    Path(file_path).write_text('name,age,city\nAlice,30,New York\nBob,25,London\n', encoding='utf-8')
    loader = CsvDictLoader(path=file_path, mode='r')

    # Run the case steps.
    loader.__enter__()
    generator = loader.yield_rows(start_line=2, end_line=2)
    result = list(generator)
    loader.__exit__(None, None, None)

    # Assert the case expectations.
    assert result == [{'name': 'Bob', 'age': '25', 'city': 'London'}]

# ** test: csv_dict_loader_save_rows_no_header
def test_csv_dict_loader_save_rows_no_header(tmp_path):
    '''
    Test that save_rows with include_header=False omits the header.

    :param tmp_path: The stage directory.
    :type tmp_path: Path
    '''

    # Prepare the stage file.
    file_path = str(tmp_path.joinpath('no_header.csv'))

    # Run the case steps.
    CsvDictLoader.save_rows(
        file_path,
        [{'name': 'Alice', 'age': '30'}],
        fieldnames=['name', 'age'],
        include_header=False,
    )
    result = CsvLoader.load_rows(file_path)

    # Assert the case expectations.
    assert result == [['Alice', '30']]
