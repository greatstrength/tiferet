"""Tiferet CSV Proxy Settings"""

# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from ...middleware import Csv, CsvDict

# *** classes

# ** class: csv_file_proxy
class CsvFileProxy(object):
    '''
    A base class for proxies that handle CSV configuration files.
    '''

    # * attribute: csv_file
    csv_file: str

    # * attribute: fieldnames
    fieldnames: List[str]

    # * attribute: encoding
    encoding: str

    # * attribute: newline
    newline: str

    # * dialect
    dialect: str

    # * delimiter
    delimiter: str

    # * quotechar
    quotechar: str

    # * escapechar
    escapechar: str

    # * doublequote
    doublequote: bool
    
    # * skipinitialspace
    skipinitialspace: bool

    # * lineterminator
    lineterminator: str

    # * quoting
    quoting: int

    # * strict
    strict: bool

    # * init
    def __init__(
        self,
        csv_file: str,
        listenames: List[str] = None,
        encoding: str = 'utf-8',
        newline: str = '',
        dialect: str = 'excel',
        delimiter: str = ',',
        quotechar: str = '"',
        escapechar: str = None,
        doublequote: bool = True,
        skipinitialspace: bool = False,
        lineterminator: str = '\r\n',
        quoting: int = 0,
        strict: bool = False
    ):
        '''
        Initialize the CsvFileProxy with CSV file settings.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param listenames: The list of field names for the CSV.
        :type listenames: List[str]
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param dialect: The CSV dialect (default is 'excel').
        :type dialect: str
        :param delimiter: The field delimiter (default is ',').
        :type delimiter: str
        :param quotechar: The character used to quote fields (default is '"').
        :type quotechar: str
        :param escapechar: The character used to escape special characters (default is None).
        :type escapechar: str
        :param doublequote: Whether to double quote fields (default is True).
        :type doublequote: bool
        :param skipinitialspace: Whether to skip spaces after delimiters (default is False).
        :type skipinitialspace: bool
        :param lineterminator: The line terminator string (default is '\r\n').
        :type lineterminator: str
        :param quoting: The quoting strategy (default is Csv.QUOTE_MINIMAL).
        :type quoting: int
        :param strict: Whether to enable strict mode (default is False).
        :type strict: bool
        '''

        # Set the CSV file and configuration attributes.
        self.csv_file = csv_file
        self.fieldnames = listenames
        self.encoding = encoding
        self.newline = newline
        self.dialect = dialect
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.doublequote = doublequote
        self.skipinitialspace = skipinitialspace
        self.lineterminator = lineterminator
        self.quoting = quoting
        self.strict = strict

    # * method: load_row
    def load_row(self, index: int) -> Dict[str, Any]:
        '''
        Load a single row from the CSV file by index.

        :param index: The index of the row to load.
        :type index: int
        :return: The row as a dict (keys match fieldnames).
        :rtype: Dict[str, Any]
        '''

        # Create a CsvDict instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='r',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_loader:
            
            # Load and return the specified row from the CSV file.
            return csv_loader.read_row(
            dialect=self.dialect,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            doublequote=self.doublequote,
            skipinitialspace=self.skipinitialspace,
            lineterminator=self.lineterminator,
            quoting=self.quoting,
            strict=self.strict
        )

    # * method: load_rows
    def load_rows(self) -> List[List[Any]]:
        '''
        Load all rows from the CSV file as a list of lists.

        :return: A list of rows, where each row is a list of values.
        :rtype: List[List[Any]]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='r',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_loader:
            
            # Load and return all rows from the CSV file.
            return csv_loader.read_all(
            dialect=self.dialect,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            doublequote=self.doublequote,
            skipinitialspace=self.skipinitialspace,
            lineterminator=self.lineterminator,
            quoting=self.quoting,
            strict=self.strict
        )

    # * method: save_row
    def save_row(self, row: List[Any]):
        '''
        Save a single row to the CSV file.

        :param row: A list of values representing the row to save.
        :type row: List[Any]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='w',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save the specified row to the CSV file.
            csv_saver.write_row(
            row,
            dialect=self.dialect,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            doublequote=self.doublequote,
            skipinitialspace=self.skipinitialspace,
            lineterminator=self.lineterminator,
            quoting=self.quoting,
            strict=self.strict
        )
            
    # * method: save_rows
    def save_rows(self, dataset: List[List[Any]]):
        '''
        Save multiple rows to the CSV file.

        :param dataset: A list of rows, where each row is a list of values.
        :type dataset: List[List[Any]]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='w',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save all rows to the CSV file.
            csv_saver.write_all(
            dataset,
            dialect=self.dialect,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            doublequote=self.doublequote,
            skipinitialspace=self.skipinitialspace,
            lineterminator=self.lineterminator,
            quoting=self.quoting,
            strict=self.strict
        )
            
    # * method: append_row
    def append_row(self, row: List[Any]):
        '''
        Append a single row to the CSV file.

        :param row: A list of values representing the row to append.
        :type row: List[Any]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='a',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_appender:
            
            # Append the specified row to the CSV file.
            csv_appender.write_row(
            row,
            dialect=self.dialect,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            doublequote=self.doublequote,
            skipinitialspace=self.skipinitialspace,
            lineterminator=self.lineterminator,
            quoting=self.quoting,
            strict=self.strict
        )