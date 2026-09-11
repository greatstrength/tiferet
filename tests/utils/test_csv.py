"""Tiferet Utils Csv Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.utils.file import FILE_NOT_FOUND_ID
from tiferet.utils.csv import (
    CsvLoader,
    CsvDictLoader,
    CSV_FIELDNAMES_REQUIRED_ID,
    CSV_INVALID_READ_MODE_ID,
    CSV_INVALID_WRITE_MODE_ID,
)

# *** fixtures

# ** fixture: sample_csv_content
@pytest.fixture
def sample_csv_content() -> str:
    '''
    Fixture providing sample CSV content as a string.

    :return: A CSV-formatted string.
    :rtype: str
    '''

    # Return sample CSV content.
    return 'name,age,city\nAlice,30,New York\nBob,25,London\nCharlie,35,Paris\n'

# ** fixture: sample_csv_rows
@pytest.fixture
def sample_csv_rows() -> list:
    '''
    Fixture providing the expected rows from the sample CSV content.

    :return: A list of list-based rows.
    :rtype: list
    '''

    # Return the expected rows.
    return [
        ['name', 'age', 'city'],
        ['Alice', '30', 'New York'],
        ['Bob', '25', 'London'],
        ['Charlie', '35', 'Paris'],
    ]

# ** fixture: temp_csv_file
@pytest.fixture
def temp_csv_file(tmp_path, sample_csv_content) -> Path:
    '''
    Fixture to create a temporary CSV file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_csv_content: The sample CSV content string.
    :type sample_csv_content: str
    :return: The path to the created temporary CSV file.
    :rtype: pathlib.Path
    '''

    # Create a temporary CSV file with sample content.
    file_path = tmp_path / 'test.csv'
    file_path.write_text(sample_csv_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: temp_empty_csv_file
@pytest.fixture
def temp_empty_csv_file(tmp_path) -> Path:
    '''
    Fixture to create an empty temporary CSV file.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created empty CSV file.
    :rtype: pathlib.Path
    '''

    # Create an empty CSV file.
    file_path = tmp_path / 'empty.csv'
    file_path.write_text('', encoding='utf-8')

    # Return the file path.
    return file_path

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

# *** testers

# ** tester: test_csv_loader
@use_tester(
    target_cls=CsvLoader,
)
class TestCsvLoader:
    '''CsvLoader binder coverage via GenericTesterContext.'''

    # * test: read_all
    def test_read_all(
            self,
            test_ctx,
            temp_csv_file: Path,
            sample_csv_rows: list,
        ) -> None:
        '''
        Test reading all rows from a CSV file.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        :param sample_csv_rows: The expected rows.
        :type sample_csv_rows: list
        '''

        # Read all rows from the CSV file.
        with test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'}) as loader:
            result = loader.read_all()

        # Verify the result matches the expected rows.
        assert result == sample_csv_rows

    # * test: read_row
    def test_read_row(self, test_ctx, temp_csv_file: Path) -> None:
        '''
        Test reading rows one at a time from a CSV file.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        '''

        # Read the first two rows individually.
        with test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'}) as loader:
            first = loader.read_row()
            second = loader.read_row()

        # Verify each row matches expected content.
        assert first == ['name', 'age', 'city']
        assert second == ['Alice', '30', 'New York']

    # * test: read_row_eof
    def test_read_row_eof(self, test_ctx, temp_empty_csv_file: Path) -> None:
        '''
        Test that reading past EOF returns an empty list.

        :param temp_empty_csv_file: The path to the empty CSV file.
        :type temp_empty_csv_file: pathlib.Path
        '''

        # Attempt to read from an empty CSV file.
        with test_ctx.make_target(
            data={'path': temp_empty_csv_file, 'mode': 'r'},
        ) as loader:
            result = loader.read_row()

        # Verify empty list is returned at EOF.
        assert result == []

    # * test: write_row
    def test_write_row(self, test_ctx, tmp_path) -> None:
        '''
        Test writing a single row to a CSV file.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Write a single row to a new CSV file.
        file_path = tmp_path / 'output.csv'
        with test_ctx.make_target(data={'path': file_path, 'mode': 'w'}) as loader:
            loader.write_row(['name', 'age'])

        # Read back and verify the content.
        with test_ctx.make_target(data={'path': file_path, 'mode': 'r'}) as loader:
            rows = loader.read_all()

        # Verify the row was written.
        assert rows == [['name', 'age']]

    # * test: write_all
    def test_write_all(self, test_ctx, tmp_path) -> None:
        '''
        Test writing multiple rows to a CSV file.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Write multiple rows.
        file_path = tmp_path / 'output.csv'
        data = [['a', 'b'], ['1', '2'], ['3', '4']]
        with test_ctx.make_target(data={'path': file_path, 'mode': 'w'}) as loader:
            loader.write_all(data)

        # Read back and verify.
        with test_ctx.make_target(data={'path': file_path, 'mode': 'r'}) as loader:
            result = loader.read_all()

        # Verify all rows were written.
        assert result == data

    # * test: save_and_reload
    def test_save_and_reload(self, tmp_path) -> None:
        '''
        Test round-trip: write rows then read them back.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Define the file path and data.
        file_path = tmp_path / 'roundtrip.csv'
        data = [['x', 'y'], ['10', '20'], ['30', '40']]

        # Save rows to CSV.
        CsvLoader.save_rows(file_path, data)

        # Reload the saved file.
        result = CsvLoader.load_rows(file_path)

        # Verify round-trip produces the same data.
        assert result == data

    # * test: load_rows_static
    def test_load_rows_static(
            self,
            temp_csv_file: Path,
            sample_csv_rows: list,
        ) -> None:
        '''
        Test the static load_rows helper.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        :param sample_csv_rows: The expected rows.
        :type sample_csv_rows: list
        '''

        # Load all rows using the static method.
        result = CsvLoader.load_rows(temp_csv_file)

        # Verify the result matches the expected rows.
        assert result == sample_csv_rows

    # * test: save_rows_static_list
    def test_save_rows_static_list(self, tmp_path) -> None:
        '''
        Test the static save_rows helper with list-based rows.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Save list rows using the static method.
        file_path = tmp_path / 'list_output.csv'
        data = [['col1', 'col2'], ['a', 'b']]
        CsvLoader.save_rows(file_path, data)

        # Reload and verify.
        result = CsvLoader.load_rows(file_path)
        assert result == data

    # * test: save_rows_dict_mode
    def test_save_rows_dict_mode(self, tmp_path) -> None:
        '''
        Test the static save_rows helper with dict-based rows.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Save dict rows using the static method.
        file_path = tmp_path / 'dict_output.csv'
        data = [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
        CsvLoader.save_rows(file_path, data, fieldnames=['name', 'age'])

        # Reload and verify (includes header row).
        result = CsvLoader.load_rows(file_path)
        assert result[0] == ['name', 'age']
        assert result[1] == ['Alice', '30']
        assert result[2] == ['Bob', '25']

    # * test: save_rows_dict_no_fieldnames
    def test_save_rows_dict_no_fieldnames(self, tmp_path) -> None:
        '''
        Test that save_rows raises CSV_FIELDNAMES_REQUIRED when writing dicts without fieldnames.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Attempt to save dict rows without fieldnames.
        file_path = tmp_path / 'dict_no_fields.csv'
        data = [{'name': 'Alice'}]

        with pytest.raises(ServiceError) as exc_info:
            CsvLoader.save_rows(file_path, data)

        # Verify the error code.
        assert exc_info.value.error_code == CSV_FIELDNAMES_REQUIRED_ID

    # * test: append_row_static
    def test_append_row_static(self, tmp_path) -> None:
        '''
        Test the static append_row helper.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create an initial CSV file with one row.
        file_path = tmp_path / 'append.csv'
        CsvLoader.save_rows(file_path, [['header1', 'header2'], ['a', 'b']])

        # Append a new row.
        CsvLoader.append_row(file_path, ['c', 'd'])

        # Reload and verify the appended row.
        result = CsvLoader.load_rows(file_path)
        assert len(result) == 3
        assert result[2] == ['c', 'd']

    # * test: yield_rows
    def test_yield_rows(
            self,
            test_ctx,
            temp_csv_file: Path,
            sample_csv_rows: list,
        ) -> None:
        '''
        Test yield_rows returns all rows as a generator.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        :param sample_csv_rows: The expected rows.
        :type sample_csv_rows: list
        '''

        # Yield all rows from the CSV file.
        with test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'}) as loader:
            result = list(loader.yield_rows())

        # Verify all rows are yielded.
        assert result == sample_csv_rows

    # * test: yield_rows_with_range
    def test_yield_rows_with_range(self, test_ctx, temp_csv_file: Path) -> None:
        '''
        Test yield_rows with start_line and end_line filtering.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        '''

        # Yield rows 2 through 3 (1-based).
        with test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'}) as loader:
            result = list(loader.yield_rows(start_line=2, end_line=3))

        # Verify only the requested range is returned.
        assert len(result) == 2
        assert result[0] == ['Alice', '30', 'New York']
        assert result[1] == ['Bob', '25', 'London']

    # * test: invalid_read_mode
    def test_invalid_read_mode(self, test_ctx, tmp_path) -> None:
        '''
        Test that building a reader in write-only mode raises CSV_INVALID_READ_MODE.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Open in write mode and attempt to build a reader.
        file_path = tmp_path / 'write_only.csv'
        with test_ctx.make_target(data={'path': file_path, 'mode': 'w'}) as loader:
            with pytest.raises(ServiceError) as exc_info:
                loader.build_reader()

        # Verify the error code.
        assert exc_info.value.error_code == CSV_INVALID_READ_MODE_ID

    # * test: invalid_write_mode
    def test_invalid_write_mode(self, test_ctx, temp_csv_file: Path) -> None:
        '''
        Test that building a writer in read-only mode raises CSV_INVALID_WRITE_MODE.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        '''

        # Open in read mode and attempt to build a writer.
        with test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'}) as loader:
            with pytest.raises(ServiceError) as exc_info:
                loader.build_writer()

        # Verify the error code.
        assert exc_info.value.error_code == CSV_INVALID_WRITE_MODE_ID

    # * test: file_not_found
    def test_file_not_found(self, test_ctx, tmp_path) -> None:
        '''
        Test that opening a non-existent CSV file raises FILE_NOT_FOUND.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Attempt to open a non-existent file.
        with pytest.raises(ServiceError) as exc_info:
            with test_ctx.make_target(
                data={'path': tmp_path / 'missing.csv', 'mode': 'r'},
            ) as loader:
                loader.read_all()

        # Verify the error code.
        assert exc_info.value.error_code == FILE_NOT_FOUND_ID

    # * test: empty_file
    def test_empty_file(self, test_ctx, temp_empty_csv_file: Path) -> None:
        '''
        Test that reading an empty CSV file returns an empty list.

        :param temp_empty_csv_file: The path to the empty CSV file.
        :type temp_empty_csv_file: pathlib.Path
        '''

        # Read all rows from the empty file.
        with test_ctx.make_target(
            data={'path': temp_empty_csv_file, 'mode': 'r'},
        ) as loader:
            result = loader.read_all()

        # Verify empty file returns empty list.
        assert result == []

    # * test: context_manager_resets_state
    def test_context_manager_resets_state(self, test_ctx, temp_csv_file: Path) -> None:
        '''
        Test that __exit__ resets reader, writer, and file to None.

        :param temp_csv_file: The path to the temporary CSV file.
        :type temp_csv_file: pathlib.Path
        '''

        # Open and use the context manager.
        loader = test_ctx.make_target(data={'path': temp_csv_file, 'mode': 'r'})
        with loader:
            loader.read_all()

        # Verify state is reset after context exit.
        assert loader.reader is None
        assert loader.writer is None
        assert loader.file is None

# ** tester: test_csv_dict_loader
@use_tester(
    target_cls=CsvDictLoader,
)
class TestCsvDictLoader:
    '''CsvDictLoader binder coverage via GenericTesterContext.'''

    # * test: read_all
    def test_read_all(self, test_ctx, temp_dict_csv_file: Path) -> None:
        '''
        Test reading all rows as dicts using CsvDictLoader.

        :param temp_dict_csv_file: The path to the temporary CSV file with header.
        :type temp_dict_csv_file: pathlib.Path
        '''

        # Read all rows as dicts.
        with test_ctx.make_target(
            data={'path': temp_dict_csv_file, 'mode': 'r'},
        ) as loader:
            result = loader.read_all()

        # Verify the result is a list of dicts.
        assert len(result) == 2
        assert result[0] == {'name': 'Alice', 'age': '30', 'city': 'New York'}
        assert result[1] == {'name': 'Bob', 'age': '25', 'city': 'London'}

    # * test: read_row
    def test_read_row(self, test_ctx, temp_dict_csv_file: Path) -> None:
        '''
        Test reading rows one at a time as dicts.

        :param temp_dict_csv_file: The path to the temporary CSV file with header.
        :type temp_dict_csv_file: pathlib.Path
        '''

        # Read the first row as a dict.
        with test_ctx.make_target(
            data={'path': temp_dict_csv_file, 'mode': 'r'},
        ) as loader:
            first = loader.read_row()
            second = loader.read_row()
            eof = loader.read_row()

        # Verify each row and EOF behavior.
        assert first == {'name': 'Alice', 'age': '30', 'city': 'New York'}
        assert second == {'name': 'Bob', 'age': '25', 'city': 'London'}
        assert eof == {}

    # * test: write_and_reload
    def test_write_and_reload(self, test_ctx, tmp_path) -> None:
        '''
        Test round-trip: write dict rows with header then read them back.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Define the file path and dict data.
        file_path = tmp_path / 'dict_roundtrip.csv'
        fieldnames = ['name', 'score']
        data = [{'name': 'X', 'score': '100'}, {'name': 'Y', 'score': '200'}]

        # Write dict rows with header.
        with test_ctx.make_target(
            data={'path': file_path, 'mode': 'w', 'fieldnames': fieldnames},
        ) as loader:
            loader.write_header()
            loader.write_all(data)

        # Reload as dicts and verify.
        with test_ctx.make_target(data={'path': file_path, 'mode': 'r'}) as loader:
            result = loader.read_all()

        # Verify round-trip.
        assert result == data

    # * test: load_rows_static
    def test_load_rows_static(self, temp_dict_csv_file: Path) -> None:
        '''
        Test the static load_rows helper on CsvDictLoader.

        :param temp_dict_csv_file: The path to the temporary CSV file with header.
        :type temp_dict_csv_file: pathlib.Path
        '''

        # Load all rows as dicts using the static method.
        result = CsvDictLoader.load_rows(temp_dict_csv_file)

        # Verify the result.
        assert len(result) == 2
        assert result[0]['name'] == 'Alice'
        assert result[1]['name'] == 'Bob'

    # * test: save_rows_static
    def test_save_rows_static(self, tmp_path) -> None:
        '''
        Test the static save_rows helper on CsvDictLoader.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Save dict rows using the static method.
        file_path = tmp_path / 'dict_save.csv'
        data = [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
        CsvDictLoader.save_rows(file_path, data, fieldnames=['a', 'b'])

        # Reload and verify.
        result = CsvDictLoader.load_rows(file_path)
        assert result == data

    # * test: save_rows_no_fieldnames
    def test_save_rows_no_fieldnames(self, tmp_path) -> None:
        '''
        Test that CsvDictLoader.save_rows raises CSV_FIELDNAMES_REQUIRED without fieldnames.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Attempt to save dict rows without fieldnames.
        file_path = tmp_path / 'no_fields.csv'
        data = [{'a': '1'}]

        with pytest.raises(ServiceError) as exc_info:
            CsvDictLoader.save_rows(file_path, data)

        # Verify the error code.
        assert exc_info.value.error_code == CSV_FIELDNAMES_REQUIRED_ID

    # * test: fieldnames_required_on_build_writer
    def test_fieldnames_required_on_build_writer(self, test_ctx, tmp_path) -> None:
        '''
        Test that building a DictWriter without fieldnames raises CSV_FIELDNAMES_REQUIRED.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Open in write mode without fieldnames.
        file_path = tmp_path / 'no_fieldnames.csv'
        with test_ctx.make_target(data={'path': file_path, 'mode': 'w'}) as loader:
            with pytest.raises(ServiceError) as exc_info:
                loader.build_writer()

        # Verify the error code.
        assert exc_info.value.error_code == CSV_FIELDNAMES_REQUIRED_ID

    # * test: yield_rows
    def test_yield_rows(self, test_ctx, temp_dict_csv_file: Path) -> None:
        '''
        Test yield_rows returns dict rows as a generator.

        :param temp_dict_csv_file: The path to the temporary CSV file with header.
        :type temp_dict_csv_file: pathlib.Path
        '''

        # Yield all dict rows.
        with test_ctx.make_target(
            data={'path': temp_dict_csv_file, 'mode': 'r'},
        ) as loader:
            result = list(loader.yield_rows())

        # Verify all dict rows are yielded.
        assert len(result) == 2
        assert result[0]['name'] == 'Alice'
        assert result[1]['name'] == 'Bob'

    # * test: yield_rows_with_range
    def test_yield_rows_with_range(self, test_ctx, temp_dict_csv_file: Path) -> None:
        '''
        Test yield_rows with range filtering on dict rows.

        :param temp_dict_csv_file: The path to the temporary CSV file with header.
        :type temp_dict_csv_file: pathlib.Path
        '''

        # Yield only the second data row (1-based, header excluded by DictReader).
        with test_ctx.make_target(
            data={'path': temp_dict_csv_file, 'mode': 'r'},
        ) as loader:
            result = list(loader.yield_rows(start_line=2, end_line=2))

        # Verify only the requested row is returned.
        assert len(result) == 1
        assert result[0]['name'] == 'Bob'

    # * test: save_rows_no_header
    def test_save_rows_no_header(self, tmp_path) -> None:
        '''
        Test that save_rows with include_header=False omits the header.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Save dict rows without header.
        file_path = tmp_path / 'no_header.csv'
        data = [{'name': 'Alice', 'age': '30'}]
        CsvDictLoader.save_rows(
            file_path,
            data,
            fieldnames=['name', 'age'],
            include_header=False,
        )

        # Reload as list rows and verify no header.
        result = CsvLoader.load_rows(file_path)
        assert len(result) == 1
        assert result[0] == ['Alice', '30']
