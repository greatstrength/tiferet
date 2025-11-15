"""Tiferet CSV Middleware Tests"""

# *** imports

# ** infra
import pytest
from _csv import Reader, Writer
from csv import DictReader, DictWriter

# ** app
from ..csv import CsvLoaderMiddleware, CsvDictLoaderMiddleware

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
        newline=''
    )

# ** fixture: csv_dict_loader_middleware
@pytest.fixture
def csv_dict_loader_middleware(temp_csv_file: str) -> CsvDictLoaderMiddleware:
    '''
    Fixture to create a CsvLoaderMiddleware instance for reading dicts.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    :return: A CsvDictLoaderMiddleware instance.
    :rtype: CsvDictLoaderMiddleware
    '''

    # Create and return a CsvLoaderMiddleware instance for dicts.
    return CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        newline=''
    )

# *** tests

# ** test: csv_list_loader_creation
def test_csv_list_loader_creation(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test the creation of a CsvLoaderMiddleware instance.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Verify that the middleware instance is created correctly.
    assert isinstance(csv_loader_middleware, CsvLoaderMiddleware)
    assert csv_loader_middleware.mode == 'r'
    assert csv_loader_middleware.encoding == 'utf-8'
    assert csv_loader_middleware.newline == ''
    assert csv_loader_middleware.file is None

# ** test: csv_list_loader_verify_mode
def test_csv_list_loader_creation_invalid_mode(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test that CsvLoaderMiddleware raises an error for invalid modes.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Attempt to create a CsvLoaderMiddleware with an invalid mode.
    with pytest.raises(ValueError) as exc_info:
        CsvLoaderMiddleware(
            path='dummy.csv',
            mode='invalid_mode',
            encoding='utf-8',
            newline=''
        )
    
    # Verify the exception message.
    assert 'Invalid mode:' in str(exc_info.value)

# ** test: csv_list_loader_build_reader
def test_csv_list_loader_build_reader(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test building a CSV reader from CsvLoaderMiddleware.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_loader_middleware as cmw:
        
        # Build the CSV reader.
        cmw.build_reader()
        
        # Verify the reader type and content.
        assert cmw.reader is not None
        assert isinstance(cmw.reader, Reader)
        assert cmw.file is not None

# ** test: csv_list_loader_build_reader_unopened_file
def test_csv_list_loader_build_reader_unopened_file(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test that building a CSV reader without opening the file raises an error.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Attempt to build a CSV reader without opening the file.
    with pytest.raises(RuntimeError) as exc_info:
        csv_loader_middleware.build_reader()
    
    # Verify the exception message.
    assert 'CSV handle not initialized.' in str(exc_info.value)

# ** test: csv_list_loader_build_reader_invalid_mode
def test_csv_list_loader_build_reader_invalid_mode(temp_csv_file: str):
    '''
    Test that building a CSV reader in an invalid mode raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in write mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Attempt to build a CSV reader in write mode.
        with pytest.raises(RuntimeError) as exc_info:
            cmw.build_reader()
        
        # Verify the exception message.
        assert 'Cannot read in mode' in str(exc_info.value)

# ** test: csv_list_loader_build_writer
def test_csv_list_loader_build_writer(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test building a CSV writer from CsvLoaderMiddleware.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Set the middleware to write mode.
    csv_loader_middleware.mode = 'w'
    
    # Use the middleware within a context to open the file.
    with csv_loader_middleware as cmw:
        
        # Build the CSV writer.
        cmw.build_writer()
        
        # Verify the writer type and content.
        assert cmw.writer is not None
        assert isinstance(cmw.writer, Writer)
        assert cmw.file is not None

# ** test: csv_list_loader_build_writer_unopened_file
def test_csv_list_loader_build_writer_unopened_file(temp_csv_file: str):
    '''
    Test that building a CSV writer without opening the file raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in write mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Attempt to build a CSV writer without opening the file.
    with pytest.raises(RuntimeError) as exc_info:
        cmw.build_writer()
    
    # Verify the exception message.
    assert 'CSV handle not initialized.' in str(exc_info.value)

# ** test: csv_list_loader_build_writer_invalid_mode
def test_csv_list_loader_build_writer_invalid_mode(temp_csv_file: str):
    '''
    Test that building a CSV writer in an invalid mode raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in read mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Attempt to build a CSV writer in read mode.
        with pytest.raises(RuntimeError) as exc_info:
            cmw.build_writer()
        
        # Verify the exception message.
        assert 'Cannot write in mode' in str(exc_info.value)

# ** test: csv_list_loader_build_reader_writer_close_file
def test_csv_list_loader_build_reader_writer_close_file(temp_csv_file: str):
    '''
    Test that building a CSV reader and writer closes the file correctly.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in read mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Build the CSV reader.
        cmw.build_reader()
        
        # Verify the file is open.
        assert cmw.file is not None

    # Verify the file is closed after exiting the context.
    assert cmw.file is None

    # Set the middleware to write mode.
    cmw.mode = 'w'
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Build the CSV writer.
        cmw.build_writer()
        
        # Verify the file is open.
        assert cmw.file is not None

    # Verify the file is closed after exiting the context.
    assert cmw.file is None

# ** test: csv_list_loader_read_row
def test_csv_list_loader_read_row(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test reading a row from the CSV using CsvLoaderMiddleware.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_loader_middleware as cmw:
        
        # Assert that the reader is None initially.
        assert cmw.reader is None

        # Read the first row.
        row, line_num = cmw.read_row()
        
        # Verify the row content.
        assert row == ['name', 'age', 'city']
        assert line_num == 1

        # Assert that the reader is now initialized.
        assert cmw.reader is not None

        # Read the second row.
        row, line_num = cmw.read_row()

        # Verify the row content.
        assert row == ['Alice', '30', 'New York']
        assert line_num == 2

# ** test: csv_list_loader_read_all
def test_csv_list_loader_read_all(csv_loader_middleware: CsvLoaderMiddleware):
    '''
    Test reading all rows from the CSV using CsvLoaderMiddleware.

    :param csv_loader_middleware: The CsvLoaderMiddleware fixture.
    :type csv_loader_middleware: CsvLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_loader_middleware as cmw:
        
        # Assert that the reader is None initially.
        assert cmw.reader is None

        # Read all rows.
        rows = cmw.read_all()
        
        # Verify the number of rows and content.
        assert len(rows) == 5
        assert rows[0] == ['name', 'age', 'city']
        assert rows[1] == ['Alice', '30', 'New York']
        assert rows[2] == ['Bob', '25', 'Los Angeles']
        assert rows[3] == ['Charlie', '35', 'Chicago']
        assert rows[4] == ['Diana', '28', 'Houston']

# ** test: csv_list_loader_save_row
def test_csv_list_loader_save_row(temp_csv_file: str):
    '''
    Test saving a row to the CSV using CsvLoaderMiddleware.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in write mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw as middleware:
        
        # Assert that the writer is None initially.
        assert middleware.writer is None

        # Save a new row.
        middleware.write_row(['name', 'age', 'city'])

        # Assert that the writer is now initialized.
        assert middleware.writer is not None

        # Save another row.
        middleware.write_row(['Eve', '22', 'Miami'])
    
    # Verify that the row was saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    
    assert content == 'name,age,city\r\nEve,22,Miami\r\n'

    # Append another row.
    cmw.mode = 'a'
    with cmw as middleware:
        middleware.write_row(['Frank', '29', 'Seattle'])

    # Verify that the appended row was saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    assert content == 'name,age,city\r\nEve,22,Miami\r\nFrank,29,Seattle\r\n'

# ** test: csv_list_loader_save_all
def test_csv_list_loader_save_all(temp_csv_file: str):
    '''
    Test saving multiple rows to the CSV using CsvLoaderMiddleware.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvLoaderMiddleware in write mode.
    cmw = CsvLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw as middleware:
        
        # Save multiple rows.
        middleware.write_all([
            ['name', 'age', 'city'],
            ['George', '40', 'Boston'],
            ['Hannah', '32', 'Denver']
        ])
    
    # Verify that the rows were saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    
    assert content == 'name,age,city\r\nGeorge,40,Boston\r\nHannah,32,Denver\r\n'

    # Append more rows.
    cmw.mode = 'a'
    with cmw as middleware:
        middleware.write_all([
            ['Ian', '27', 'Austin'],
            ['Jane', '31', 'San Francisco']
        ])

    # Verify that the appended rows were saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    assert content == 'name,age,city\r\nGeorge,40,Boston\r\nHannah,32,Denver\r\nIan,27,Austin\r\nJane,31,San Francisco\r\n'

# ** test: csv_dict_loader_creation
def test_csv_dict_loader_creation(csv_dict_loader_middleware: CsvDictLoaderMiddleware):
    '''
    Test the creation of a CsvDictLoaderMiddleware instance.

    :param csv_dict_loader_middleware: The CsvDictLoaderMiddleware fixture.
    :type csv_dict_loader_middleware: CsvDictLoaderMiddleware
    '''

    # Verify that the middleware instance is created correctly.
    assert isinstance(csv_dict_loader_middleware, CsvDictLoaderMiddleware)
    assert csv_dict_loader_middleware.mode == 'r'
    assert csv_dict_loader_middleware.encoding == 'utf-8'
    assert csv_dict_loader_middleware.newline == ''
    assert csv_dict_loader_middleware.file is None

# ** test: csv_dict_loader_build_reader
def test_csv_dict_loader_build_reader(csv_dict_loader_middleware: CsvDictLoaderMiddleware):
    '''
    Test building a CSV Dict reader from CsvDictLoaderMiddleware.

    :param csv_dict_loader_middleware: The CsvDictLoaderMiddleware fixture.
    :type csv_dict_loader_middleware: CsvDictLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_dict_loader_middleware as cmw:
        
        # Build the CSV Dict reader.
        cmw.build_reader()
        
        # Verify the reader type and content.
        assert cmw.reader is not None
        assert isinstance(cmw.reader, DictReader)
        assert cmw.file is not None

# ** test: csv_dict_loader_unopened_file
def test_csv_dict_loader_unopened_file(csv_dict_loader_middleware: CsvDictLoaderMiddleware):
    '''
    Test that building a CSV Dict reader without opening the file raises an error.

    :param csv_dict_loader_middleware: The CsvDictLoaderMiddleware fixture.
    :type csv_dict_loader_middleware: CsvDictLoaderMiddleware
    '''

    # Attempt to build a CSV Dict reader without opening the file.
    with pytest.raises(RuntimeError) as exc_info:
        csv_dict_loader_middleware.build_reader()
    
    # Verify the exception message.
    assert 'CSV handle not initialized.' in str(exc_info.value)

# ** test: csv_dict_loader_invalid_mode
def test_csv_dict_loader_invalid_mode(temp_csv_file: str):
    '''
    Test that building a CSV Dict reader in an invalid mode raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Attempt to build a CSV Dict reader in write mode.
        with pytest.raises(RuntimeError) as exc_info:
            cmw.build_reader()
        
        # Verify the exception message.
        assert 'Cannot read in mode' in str(exc_info.value)

# ** test: csv_dict_loader_build_writer
def test_csv_dict_loader_build_writer(temp_csv_file: str):
    '''
    Test building a CSV Dict writer from CsvDictLoaderMiddleware.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw as cmw:
        
        # Build the CSV Dict writer.
        cmw.build_writer(fieldnames=['name', 'age', 'city'])
        
        # Verify the writer type and content.
        assert cmw.writer is not None
        assert isinstance(cmw.writer, DictWriter)
        assert cmw.file is not None

# ** test: csv_dict_loader_build_writer_unopened_file
def test_csv_dict_loader_build_writer_unopened_file(temp_csv_file: str):
    '''
    Test that building a CSV Dict writer without opening the file raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Attempt to build a CSV Dict writer without opening the file.
    with pytest.raises(RuntimeError) as exc_info:
        cmw.build_writer(fieldnames=['name', 'age', 'city'])
    
    # Verify the exception message.
    assert 'CSV handle not initialized.' in str(exc_info.value)

# ** test: csv_dict_loader_build_writer_invalid_mode
def test_csv_dict_loader_build_writer_invalid_mode(temp_csv_file: str):
    '''
    Test that building a CSV Dict writer in an invalid mode raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in read mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='r',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Attempt to build a CSV Dict writer in read mode.
        with pytest.raises(RuntimeError) as exc_info:
            cmw.build_writer(fieldnames=['name', 'age', 'city'])
        
        # Verify the exception message.
        assert 'Cannot write in mode' in str(exc_info.value)

# ** test: csv_dict_loader_build_writer_no_fieldnames
def test_csv_dict_loader_build_writer_no_fieldnames(temp_csv_file: str):
    '''
    Test that building a CSV Dict writer without fieldnames raises an error.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw:
        
        # Attempt to build a CSV Dict writer without fieldnames.
        with pytest.raises(ValueError) as exc_info:
            cmw.build_writer(fieldnames=None)
        
        # Verify the exception message.
        assert 'Fieldnames must be provided for DictWriter.' in str(exc_info.value)

# ** test: csv_dict_loader_read_row
def test_csv_dict_loader_read_row(csv_dict_loader_middleware: CsvDictLoaderMiddleware):
    '''
    Test reading a row from the CSV as a dict using CsvDictLoaderMiddleware.

    :param csv_dict_loader_middleware: The CsvDictLoaderMiddleware fixture.
    :type csv_dict_loader_middleware: CsvDictLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_dict_loader_middleware as cmw:
        
        # Read the first row.
        row, line_num = cmw.read_row()
        
        # Verify the row content.
        assert isinstance(row, dict)
        assert row == {'name': 'Alice', 'age': '30', 'city': 'New York'}
        assert line_num == 2

# ** test: csv_dict_loader_read_all
def test_csv_dict_loader_read_all(csv_dict_loader_middleware: CsvDictLoaderMiddleware):
    '''
    Test reading all rows from the CSV as dicts using CsvDictLoaderMiddleware.

    :param csv_dict_loader_middleware: The CsvDictLoaderMiddleware fixture.
    :type csv_dict_loader_middleware: CsvDictLoaderMiddleware
    '''

    # Use the middleware within a context to open the file.
    with csv_dict_loader_middleware as cmw:
        
        # Read all rows.
        rows = cmw.read_all()
        
        # Verify the number of rows and content.
        assert len(rows) == 4
        assert rows[0] == {'name': 'Alice', 'age': '30', 'city': 'New York'}
        assert rows[1] == {'name': 'Bob', 'age': '25', 'city': 'Los Angeles'}
        assert rows[2] == {'name': 'Charlie', 'age': '35', 'city': 'Chicago'}
        assert rows[3] == {'name': 'Diana', 'age': '28', 'city': 'Houston'}

# ** test: csv_dict_loader_save_row
def test_csv_dict_loader_save_row(temp_csv_file: str):
    '''
    Test saving a dict row to the CSV using CsvDictLoaderMiddleware.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw as middleware:
        
        # Save a new dict row.
        middleware.write_row(
            {'name': 'Kate', 'age': '26', 'city': 'Philadelphia'},
            fieldnames=['name', 'age', 'city']
        )
    
    # Verify that the dict row was saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    
    assert content == 'name,age,city\r\nKate,26,Philadelphia\r\n'

    # Append another dict row.
    cmw.mode = 'a'
    with cmw as middleware:
        middleware.write_row(
            {'name': 'Leo', 'age': '33', 'city': 'San Diego'},
            fieldnames=['name', 'age', 'city'],
            include_header=False
        )

    # Verify that the appended dict row was saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    assert content == 'name,age,city\r\nKate,26,Philadelphia\r\nLeo,33,San Diego\r\n'

# ** test: csv_dict_loader_write_all
def test_csv_dict_loader_write_all(temp_csv_file: str):
    '''
    Test saving multiple dict rows to the CSV using CsvDictLoaderMiddleware.

    :param temp_csv_file: The path to the temporary CSV file.
    :type temp_csv_file: str
    '''

    # Create a CsvDictLoaderMiddleware in write mode.
    cmw = CsvDictLoaderMiddleware(
        path=temp_csv_file,
        mode='w',
        encoding='utf-8',
        newline=''
    )
    
    # Use the middleware within a context to open the file.
    with cmw as middleware:
        
        # Save multiple dict rows.
        middleware.write_all([
            {'name': 'Mia', 'age': '29', 'city': 'Orlando'},
            {'name': 'Noah', 'age': '34', 'city': 'Portland'}
        ], fieldnames=['name', 'age', 'city'])
    
    # Verify that the dict rows were saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    
    assert content == 'name,age,city\r\nMia,29,Orlando\r\nNoah,34,Portland\r\n'

    # Append more dict rows.
    cmw.mode = 'a'
    with cmw as middleware:
        middleware.write_all([
                {'name': 'Olivia', 'age': '24', 'city': 'Nashville'},
                {'name': 'Paul', 'age': '38', 'city': 'Cleveland'}
            ],
            fieldnames=['name', 'age', 'city'],
            include_header=False
        )

    # Verify that the appended dict rows were saved correctly.
    with open(temp_csv_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    assert content == 'name,age,city\r\nMia,29,Orlando\r\nNoah,34,Portland\r\nOlivia,24,Nashville\r\nPaul,38,Cleveland\r\n'