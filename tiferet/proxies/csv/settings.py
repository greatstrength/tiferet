"""Tiferet CSV Proxy Settings"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any,
    Callable
)

# ** app
from ...commands import RaiseError
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

    # * csv_settings
    csv_settings: Dict[str, Any]

    # * init
    def __init__(
        self,
        csv_file: str,
        fieldnames: List[str] = None,
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        Initialize the CsvFileProxy with CSV file settings.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param fieldnames: The list of field names for the CSV.
        :type fieldnames: List[str]
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Set the CSV file and configuration attributes.
        self.csv_file = csv_file
        self.fieldnames = fieldnames
        self.encoding = encoding
        self.newline = newline
        self.csv_settings = csv_settings

    # * method: get_start_line_num
    def get_start_line_num(self, start_index: int = None, has_header: bool = True) -> int:
        '''
        Get the starting line number for reading CSV rows.

        :param start_index: The starting index for reading rows (default is None).
        :type start_index: int
        :param has_header: Whether the CSV file has a header row (default is True).
        :type has_header: bool
        :return: The starting line number.
        :rtype: int
        '''

        # Determine the starting line number based on the presence of a header.
        if not start_index:
            return 2 if has_header else 1
        if has_header:
            return start_index + 2
        else:
            return start_index + 1
        
    # me:thod: get_end_line_num
    def get_end_line_num(self, end_index: int = None, has_header: bool = True) -> int:
        '''
        Get the ending line number for reading CSV rows.

        :param end_index: The non-inclusive ending index for reading rows (default is None).
        :type end_index: int
        :param has_header: Whether the CSV file has a header row (default is True).
        :type has_header: bool
        :return: The ending line number.
        :rtype: int
        '''

        # Determine the ending line number based on the presence of a header.
        if end_index and has_header:
            return end_index + 2
        elif not has_header:
            return end_index + 1
        else:
            return -1
        
    # * method: yield_rows
    def yield_rows(self,
        csv_loader: Csv,
        start_line_num: int = 1,
        end_line_num: int = -1,
    ):
        '''
        A generator function to yield rows from the CSV file within a specified line number range.

        :param csv_loader: An instance of the Csv class for reading the CSV file.
        :type csv_loader: Csv
        :param start_line_num: The starting line number for reading rows.
        :type start_line_num: int
        :param end_line_num: The non-inclusive ending line number for reading rows.
        :type end_line_num: int
        '''

        # Read rows one by one.
        while True:
            row, line_num = csv_loader.read_row(
                **self.csv_settings
            )

            # Break the loop if there are no more rows or we reached the end index.
            if line_num == -1 or line_num == end_line_num:
                break

            # Yield the row if it falls within the specified line number range.
            if start_line_num <= line_num < (end_line_num if end_line_num != -1 else float('inf')):
                yield row

    # * method: load_rows
    def load_rows(self, 
        is_dict: bool = False,
        start_index: int = None,
        end_index: int = None,
        has_header: bool = True,
        data_factory: Callable = lambda data: data
    ) -> List[Any]:
        '''
        Load rows from the CSV file.

        :param is_dict: Whether to load rows as dictionaries (default is False).
        :type is_dict: bool
        :param start_index: The starting index for loading rows (default is None).
        :type start_index: int
        :param end_index: The non-inclusive ending index for loading rows (default is None).
        :type end_index: int
        :param has_header: Whether the CSV file has a header row (default is True).
        :type has_header: bool
        :param data_factory: A callable to process each row after loading (default is identity).
        :type data_factory: Callable
        :return: A list of loaded rows.
        :rtype: List[Any]
        '''

        # Raise an error if rows are loaded as dicts with no header.
        if is_dict and not has_header:
            RaiseError.execute(
                'CSV_DICT_NO_HEADER',
                'Cannot load CSV rows as dictionaries when has_header is False.',
                csv_file=self.csv_file
            )

        # Determine whether to use CsvDict or Csv based on is_dict flag.
        CsvClass = CsvDict if is_dict else Csv

        # Create a Csv instance with the configured settings.
        with CsvClass(
            path=self.csv_file,
            mode='r',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_loader:
            
            # Load and return all rows from the CSV file if the start and end indices are not specified.
            if start_index is None and end_index is None:
                return [data_factory(row) for row in csv_loader.read_all(
                    **self.csv_settings
                )]
            
            # Specify the start line number.
            start_line_num = self.get_start_line_num(
                start_index=start_index,
                has_header=has_header
            )

            # Specify the end line number.
            end_line_num = self.get_end_line_num(
                end_index=end_index,
                has_header=has_header
            )

            # Return the list of rows from the generator.
            return list(self.yield_rows(
                csv_loader=csv_loader,
                start_line_num=start_line_num,
                end_line_num=end_line_num
            ))

    # * method: append_row
    def append_row(self, row: List[Any]):
        '''
        Save a single row to the CSV file.

        :param row: A list of values representing the row to save.
        :type row: List[Any]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode='a',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save the specified row to the CSV file.
            csv_saver.write_row(
            row,
            **self.csv_settings
        )
            
    # * method: append_dict_row
    def append_dict_row(self, row: Dict[str, Any]):
        '''
        Save a single dictionary row to the CSV file.

        :param row: A dictionary representing the row to save (keys match fieldnames).
        :type row: Dict[str, Any]
        '''

        # Create a CsvDict instance with the configured settings.
        with CsvDict(
            path=self.csv_file,
            mode='a',
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save the specified dictionary row to the CSV file.
            csv_saver.write_row(
            row,
            fieldnames=self.fieldnames,
            include_header=False,
            **self.csv_settings
        )
            
    # * method: save_rows
    def save_rows(self, dataset: List[List[Any]], mode: str = 'w'):
        '''
        Save multiple rows to the CSV file.

        :param dataset: A list of rows, where each row is a list of values.
        :type dataset: List[List[Any]]
        '''

        # Create a Csv instance with the configured settings.
        with Csv(
            path=self.csv_file,
            mode=mode,
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save all rows to the CSV file.
            csv_saver.write_all(
            dataset,
            **self.csv_settings
        )
            
    # * method: save_dict_rows
    def save_dict_rows(self, dataset: List[Dict[str, Any]], mode: str = 'w'):
        '''
        Save multiple dictionary rows to the CSV file.

        :param dataset: A list of dictionary rows (keys match fieldnames).
        :type dataset: List[Dict[str, Any]]
        '''

        # Determine whether to include the header based on the mode.
        include_header = True if mode == 'w' else False

        # Create a CsvDict instance with the configured settings.
        with CsvDict(
            path=self.csv_file,
            mode=mode,
            encoding=self.encoding,
            newline=self.newline
        ) as csv_saver:
            
            # Save all dictionary rows to the CSV file.
            csv_saver.write_all(
            dataset,
            fieldnames=self.fieldnames,
            include_header=include_header,
            **self.csv_settings
        )