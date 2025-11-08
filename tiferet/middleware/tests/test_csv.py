"""Tiferet CSV Middleware Tests"""

# *** imports
import pytest

# ** app
from ..csv import CsvLoaderMiddleware

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

# ** fixture: csv_loader_middleware
@pytest.fixture
def csv_loader_middleware(temp_csv_file: str) -> CsvLoaderMiddleware:
    '''
    Fixture to create a CsvLoaderMiddleware instance for reading.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    :return: A CsvLoaderMiddleware instance.
    :rtype: CsvLoaderMiddleware
    '''

    # Create and return a CsvLoaderMiddleware instance.
    return CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        delimiter=',',
        newline='',
        use_dict=True,
    )