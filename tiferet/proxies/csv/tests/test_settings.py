"""Tiferet CSV Proxy Settings Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ....commands import TiferetError
from ....middleware import Csv, CsvDict
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
    with Csv(path=str(file_path), mode='w', encoding='utf-8', newline='') as csv_w:
        csv_w.write_row(['name', 'age', 'city'])
        csv_w.write_row(['Alice', '30', 'New York'])
        csv_w.write_row(['Bob', '25', 'Los Angeles'])
        csv_w.write_row(['Charlie', '35', 'Chicago'])
        csv_w.write_row(['Diana', '28', 'Miami'])
    
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

# *** tests

# ** test: csv_file_proxy_creation
def test_csv_file_proxy_creation(csv_file_proxy: CsvFileProxy):
    '''
    Test the creation of a CsvFileProxy instance.

    :param csv_file_proxy: The CsvFileProxy fixture.
    :type csv_file_proxy: CsvFileProxy
    '''

    # Verify that the proxy instance is created correctly.
    pass