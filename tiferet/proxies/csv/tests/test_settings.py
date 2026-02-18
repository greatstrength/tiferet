"""Tiferet CSV Proxy Settings Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ....assets import TiferetError
from ....utils import CsvDict
from ..settings import CsvFileProxy

# *** fixtures

# ** fixture: temp_csv_file
@pytest.fixture
def temp_csv_file(tmp_path):
    '''
    Fixture to create a temporary CSV file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary CSV file.
    :rtype: str
    '''

    # Create a temporary CSV file with sample content.
    file_path = tmp_path / 'test.csv'
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write('name,age,city\n')
        f.write('Alice,30,New York\n')
        f.write('Bob,25,Los Angeles\n')
        f.write('Charlie,35,Chicago\n')
        f.write('Diana,28,Houston\n')
    
    # Return the file path as a string.
    return str(file_path)

# ** fixture: tmp_csv_file_no_header
@pytest.fixture
def tmp_csv_file_no_header(tmp_path):
    '''
    Fixture to create a temporary CSV file without a header.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created temporary CSV file without a header.
    :rtype: str
    '''

    # Create a temporary CSV file without a header.
    file_path = tmp_path / 'test_no_header.csv'
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write('Alice,30,New York\n')
        f.write('Bob,25,Los Angeles\n')
        f.write('Charlie,35,Chicago\n')
        f.write('Diana,28,Houston\n')
    
    # Return the file path as a string.
    return str(file_path)

# ** fixture: csv_file_proxy
@pytest.fixture
def csv_file_proxy(temp_csv_file: str) -> CsvFileProxy:
    '''
    Fixture to create a CsvFileProxy instance.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    :return: A CsvFileProxy instance.
    :rtype: CsvFileProxy
    '''

    # Create and return a CsvFileProxy instance.
    return CsvFileProxy(
        csv_file=temp_csv_file,
        fieldnames=['name', 'age', 'city'],
        encoding='utf-8',
        newline=''
    )

# ** fixture: csv_dict_loader_read
@pytest.fixture
def csv_dict_loader_read(temp_csv_file: str) -> CsvDict:
    '''
    Fixture to create a CsvDict loader for reading the temporary CSV file.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    :return: A CsvDict loader instance.
    :rtype: CsvDict
    '''

    # Create and return a CsvDict loader instance for reading.
    return CsvDict(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        newline=''
    )

# *** tests

# ** test: csv_file_proxy_creation
def test_csv_file_proxy_creation(csv_file_proxy: CsvFileProxy):
    '''
    Test the creation of a CsvFileProxy instance.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Verify that the proxy instance is created correctly.
    assert isinstance(csv_file_proxy, CsvFileProxy)
    assert csv_file_proxy.csv_file is not None
    assert csv_file_proxy.fieldnames == ['name', 'age', 'city']
    assert csv_file_proxy.encoding == 'utf-8'
    assert csv_file_proxy.newline == ''

# ** test: csv_file_proxy_get_start_line_num
def test_csv_file_proxy_get_start_line_num(csv_file_proxy: CsvFileProxy):
    '''
    Test the get_start_line_num method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Test with has_header = True.
    start_line_num = csv_file_proxy.get_start_line_num(has_header=True)
    assert start_line_num == 2  # Header line + 1

    # Test with has_header = False.
    start_line_num = csv_file_proxy.get_start_line_num(has_header=False)
    assert start_line_num == 1  # No header, start from line 1

    # Test with start_index provided.
    start_line_num = csv_file_proxy.get_start_line_num(start_index=3, has_header=True)
    assert start_line_num == 5  # Use provided start_index

    # Test with start_index provided and has_header = False.
    start_line_num = csv_file_proxy.get_start_line_num(start_index=3, has_header=False)
    assert start_line_num == 4  # Use provided start_index

# ** test: csv_file_proxy_get_end_line_num
def test_csv_file_proxy_get_end_line_num(csv_file_proxy: CsvFileProxy):
    '''
    Test the get_end_line_num method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Test with no end_index provided.
    end_line_num = csv_file_proxy.get_end_line_num()
    assert end_line_num == -1  # No end_index provided

    # Test with end_index provided.
    end_line_num = csv_file_proxy.get_end_line_num(end_index=3, has_header=True)
    assert end_line_num == 5  # Use provided end_index

    # Test with end_index provided and has_header = False
    end_line_num = csv_file_proxy.get_end_line_num(end_index=3, has_header=False)
    assert end_line_num == 4  # Use provided end_index

# ** test: csv_file_proxy_yield_rows
def test_csv_file_proxy_yield_rows(csv_file_proxy: CsvFileProxy, csv_dict_loader_read: CsvDict):
    '''
    Test the yield_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Test yielding all rows.
    with csv_dict_loader_read as csv_loader:
        rows = list(csv_file_proxy.yield_rows(csv_loader=csv_loader))
        assert len(rows) == 4  # 4 data rows
        assert rows == [
            {'name': 'Alice', 'age': '30', 'city': 'New York'},
            {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'},
            {'name': 'Charlie', 'age': '35', 'city': 'Chicago'},
            {'name': 'Diana', 'age': '28', 'city': 'Houston'}
        ]

    # Test yielding rows with start number.
    with csv_dict_loader_read as csv_loader:
        rows = list(csv_file_proxy.yield_rows(csv_loader=csv_loader, start_line_num=4))
        assert len(rows) == 2  # Rows from line 3 onwards
        assert rows == [
            {'name': 'Charlie', 'age': '35', 'city': 'Chicago'},
            {'name': 'Diana', 'age': '28', 'city': 'Houston'}
        ]

    # Test yielding rows with end number.
    with csv_dict_loader_read as csv_loader:
        rows = list(csv_file_proxy.yield_rows(csv_loader=csv_loader, end_line_num=4))
        assert len(rows) == 2  # Rows up to line 3
        assert rows == [
            {'name': 'Alice', 'age': '30', 'city': 'New York'},
            {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'}
        ]

    # Test yielding rows with start and end numbers.
    with csv_dict_loader_read as csv_loader:
        rows = list(csv_file_proxy.yield_rows(csv_loader=csv_loader, start_line_num=3, end_line_num=5))
        assert len(rows) == 2  # Rows from line 2 to line 4
        assert rows == [
            {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'},
            {'name': 'Charlie', 'age': '35', 'city': 'Chicago'}
        ]

# ** test: csv_file_proxy_load_rows
def test_csv_file_proxy_load_rows(csv_file_proxy: CsvFileProxy):
    '''
    Test the load_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Test loading all rows as dicts.
    rows = csv_file_proxy.load_rows(is_dict=True)
    assert len(rows) == 4  # 4 data rows
    assert rows == [
        {'name': 'Alice', 'age': '30', 'city': 'New York'},
        {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'},
        {'name': 'Charlie', 'age': '35', 'city': 'Chicago'},
        {'name': 'Diana', 'age': '28', 'city': 'Houston'}
    ]

    # Test loading rows with start and end indices.
    rows = csv_file_proxy.load_rows(is_dict=True, start_index=1, end_index=3)
    assert len(rows) == 2  # Rows from index 1 to 2
    assert rows == [
        {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'},
        {'name': 'Charlie', 'age': '35', 'city': 'Chicago'}
    ]

# ** test: csv_file_proxy_load_rows_dict_with_no_header_error
def test_csv_file_proxy_load_rows_dict_with_no_header_error(csv_file_proxy: CsvFileProxy):
    '''
    Test that loading rows as dicts without a header raises an error.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Attempt to load rows as dicts with has_header = False and expect an error.
    with pytest.raises(TiferetError) as exc_info:
        csv_file_proxy.load_rows(is_dict=True, has_header=False)
    
    # Verify the error message.
    assert exc_info.value.error_code == 'CSV_DICT_NO_HEADER'
    assert 'Cannot load CSV rows as dictionaries when has_header is False.' in str(exc_info.value)
    assert exc_info.value.kwargs.get('csv_file') == csv_file_proxy.csv_file

# ** test: csv_file_proxy_load_rows_list_no_header
def test_csv_file_proxy_load_rows_list_no_header(csv_file_proxy: CsvFileProxy, tmp_csv_file_no_header: str):
    '''
    Test loading rows as lists without a header.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Set the CSV file to the one without a header.
    csv_file_proxy.csv_file = tmp_csv_file_no_header

    # Test loading all rows as lists without a header.
    rows = csv_file_proxy.load_rows(is_dict=False, has_header=False)
    assert len(rows) == 4  # 4 data rows
    assert rows == [
        ['Alice', '30', 'New York'],
        ['Bob', '25', 'Los Angeles'],
        ['Charlie', '35', 'Chicago'],
        ['Diana', '28', 'Houston']
    ]

    # Test loading rows with start and end indices.
    rows = csv_file_proxy.load_rows(is_dict=False, start_index=1, end_index=3, has_header=False)
    assert len(rows) == 2  # Rows from index 1 to 2
    assert rows == [
        ['Bob', '25', 'Los Angeles'],
        ['Charlie', '35', 'Chicago']
    ]

# ** test: csv_file_proxy_append_row
def test_csv_file_proxy_append_row(csv_file_proxy: CsvFileProxy):
    '''
    Test the append_row method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new row to append as a list.
    new_row = ['Eve', '32', 'Miami']

    # Append the new row.
    csv_file_proxy.append_row(row=new_row)

    # Load all rows to verify the new row was appended.
    rows = csv_file_proxy.load_rows(is_dict=False)
    assert len(rows) == 6  # 5 original rows (including header) + 1 appended row
    assert rows[-1] == new_row  # Verify the last row is the new row

# ** test: csv_file_proxy_append_dict_row
def test_csv_file_proxy_append_dict_row(csv_file_proxy: CsvFileProxy):
    '''
    Test the append_row method of CsvFileProxy with a dictionary row.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new row to append as a dictionary.
    new_row = {'name': 'Eve', 'age': '32', 'city': 'Miami'}

    # Append the new row.
    csv_file_proxy.append_dict_row(row=new_row)

    # Load all rows to verify the new row was appended.
    rows = csv_file_proxy.load_rows(is_dict=True)
    assert len(rows) == 5  # 4 original rows (with header included as key) + 1 appended row
    assert rows[-1] == new_row  # Verify the last row is the new row

# ** test: csv_file_proxy_save_rows
def test_csv_file_proxy_save_rows(csv_file_proxy: CsvFileProxy):
    '''
    Test the save_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new dataset to save.
    new_dataset = [
        ['name', 'age', 'city'],
        ['Frank', '40', 'Seattle'],
        ['Grace', '29', 'Boston']
    ]

    # Save the new dataset.
    csv_file_proxy.save_rows(dataset=new_dataset, mode='w')

    # Load all rows to verify the dataset was saved correctly.
    rows = csv_file_proxy.load_rows()
    assert len(rows) == 3  # 3 rows in the new dataset (including header)
    assert rows == new_dataset  # Verify the loaded rows match the new dataset

# ** test: csv_file_proxy_save_rows_append
def test_csv_file_proxy_save_rows_append(csv_file_proxy: CsvFileProxy):
    '''
    Test appending rows using the save_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new dataset to append.
    new_dataset = [
        ['Frank', '40', 'Seattle'],
        ['Grace', '29', 'Boston']
    ]

    # Append the new dataset.
    csv_file_proxy.save_rows(dataset=new_dataset, mode='a')

    # Load all rows to verify the dataset was appended correctly.
    rows = csv_file_proxy.load_rows()
    assert len(rows) == 7  # 5 original rows (including header) + 2 appended rows
    assert rows[-2:] == new_dataset  # Verify the last two rows are the new dataset

# ** test: csv_file_proxy_save_dict_rows
def test_csv_file_proxy_save_dict_rows(csv_file_proxy: CsvFileProxy):
    '''
    Test the save_dict_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new dataset to save as dictionaries.
    new_dataset = [
        {'name': 'Frank', 'age': '40', 'city': 'Seattle'},
        {'name': 'Grace', 'age': '29', 'city': 'Boston'}
    ]

    # Save the new dataset.
    csv_file_proxy.save_dict_rows(dataset=new_dataset, mode='w')

    # Load all rows to verify the dataset was saved correctly.
    rows = csv_file_proxy.load_rows(is_dict=True)
    assert len(rows) == 2  # 2 rows in the new dataset
    assert rows == new_dataset  # Verify the loaded rows match the new dataset

# ** test: csv_file_proxy_save_dict_rows_append
def test_csv_file_proxy_save_dict_rows_append(csv_file_proxy: CsvFileProxy):
    '''
    Test appending dictionary rows using the save_dict_rows method of CsvFileProxy.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Define a new dataset to append as dictionaries.
    new_dataset = [
        {'name': 'Frank', 'age': '40', 'city': 'Seattle'},
        {'name': 'Grace', 'age': '29', 'city': 'Boston'}
    ]

    # Append the new dataset.
    csv_file_proxy.save_dict_rows(dataset=new_dataset, mode='a')

    # Load all rows to verify the dataset was appended correctly.
    rows = csv_file_proxy.load_rows(is_dict=True)
    assert len(rows) == 6  # 4 original rows + 2 appended rows
    assert rows[-2:] == new_dataset  # Verify the last two rows are the new dataset