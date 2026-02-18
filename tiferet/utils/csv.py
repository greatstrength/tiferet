"""Tiferet CSV Utilities"""

# *** imports
import csv
from _csv import Reader, Writer
from typing import (
    List,
    Dict,
    Tuple,
    Any,
    Callable
)

# ** app
from .file import FileLoader
from ..events import RaiseError
from .. import assets as a

# *** utils

# ** util: csv_loader
class CsvLoader(FileLoader):
    '''
    CSV-specific middleware built on top of FileLoaderMiddleware.
    Supports list-based rows (csv.reader / csv.writer) **and**
    dict-based rows (csv.DictReader / csv.DictWriter) with configurable
    delimiter, newline handling and optional field-names.
    '''

    # * attribute: reader
    reader: Reader

    # * attribute: writer
    writer: Writer

    # * init
    def __init__(
        self,
        path: str,
        mode: str = 'r',
        encoding: str = 'utf-8',
        newline: str = ''
    ):
        '''
        Initialize the CsvLoader with a file path, mode, encoding, and newline handling.
        
        :param path: The path to the CSV file to load.
        :type path: str
        :param mode: The mode in which to open the file (default is 'r' for read).
        :type mode: str
        :param encoding: The encoding to use when reading the file (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter to use when opening the file (default is '').
        :type newline: str
        '''

        # Verify the CSV-compatible file mode.
        self.verify_mode(mode)

        # Call the parent class initializer.
        super().__init__(path=path, mode=mode, encoding=encoding, newline=newline)

        # Set the CSV reader and writer to None initially.
        self.reader = None
        self.writer = None

    # * method: verify_mode
    def verify_mode(self, mode: str):
        '''
        Verify the file mode is compatible with the csv module.
        
        :param mode: The file mode.
        :type mode: str
        '''

        # Valid CSV modes.
        valid_modes = ['r', 'w', 'a', 'r+', 'w+', 'a+']
        if mode not in valid_modes:
            RaiseError.execute(
                a.const.CSV_INVALID_MODE_ID,
                f'Invalid mode: {mode!r}. CSV supports: {", ".join(sorted(valid_modes))}',
                mode=mode
            )

    # * method: build_reader
    def build_reader(self, **kwargs):
        '''
        Build a CSV reader list from the opened file.

        :param kwargs: Additional keyword arguments for csv.reader.
        :type kwargs: dict
        '''

        # Ensure the file is opened.
        if self.file is None:
            RaiseError.execute(
                a.const.CSV_HANDLE_NOT_INITIALIZED_ID,
                'CSV handle not initialized. Use within "with" block.'
            )

        # Ensure the mode is readable.
        if self.mode[0] not in {'r'}:
            RaiseError.execute(
                a.const.CSV_INVALID_READ_MODE_ID,
                f'Cannot read in mode {self.mode!r}',
                mode=self.mode
            )
        
        # Else build a standard CSV reader and set the reader attribute.
        self.reader = csv.reader(self.file, **kwargs)

    # * method: build_writer
    def build_writer(self, **kwargs):
        '''
        Build a CSV writer (list or dict) for the opened file.

        :param kwargs: Additional keyword arguments for csv.writer.
        :type kwargs: dict
        '''

        # Ensure the file is opened.
        if self.file is None:
            RaiseError.execute(
                a.const.CSV_HANDLE_NOT_INITIALIZED_ID,
                'CSV handle not initialized. Use within "with" block.'
            )

        # Ensure the mode is writable.
        if self.mode[0] not in {'w', 'a'}:
            RaiseError.execute(
                a.const.CSV_INVALID_WRITE_MODE_ID,
                f'Cannot write in mode {self.mode!r}',
                mode=self.mode
            )

        # Build a standard CSV writer and set the writer attribute.
        self.writer = csv.writer(self.file, **kwargs)

    # * method: close_file
    def close_file(self):
        '''
        Close the CSV file and reset the reader and writer attributes.
        '''

        # Call the parent class method to close the file.
        super().close_file()

        # Reset the CSV reader and writer to None.
        self.reader = None
        self.writer = None
    
    # * method: read_row
    def read_row(self, **kwargs) -> Tuple[List[Any], int]:
        '''
        Read a single row from the CSV file as a list with its line number.

        :param kwargs: Additional keyword arguments for csv.reader.
        :type kwargs: dict
        :return: A single row from the CSV file.
        :rtype: List[Any]
        '''
        
        # Build a CSV reader if not provided.
        if not self.reader:
            self.build_reader(**kwargs)

        # Read and return a single row.
        try:
            return next(self.reader), self.reader.line_num
        
        # Handle end of file.
        except StopIteration:
            return None, -1
    
    # * method: read_all
    def read_all(self, **kwargs) -> List[List[Any]]:
        '''
        Read all rows from the CSV file as a list of lists.

        :param kwargs: Additional keyword arguments for csv.reader.
        :type kwargs: dict
        :return: All rows from the CSV file.
        :rtype: List[List[Any]]
        '''

        # Build a CSV reader.
        self.build_reader(**kwargs)

        # Read and return all rows.
        return list(self.reader)

    # * method: write_row
    def write_row(self, row: List[Any], **kwargs):
        '''
        Write a single row to the CSV file.
        
        :param row: A dict (keys match fieldnames) or list of values.
        :type row: dict | list
        :param include_header: Write header row before the row (DictWriter only).
        :type include_header: bool
        '''

        # Build a CSV writer if not present.
        if not self.writer:
            self.build_writer(**kwargs)

        # Write the row.
        self.writer.writerow(row)

    # * method: save_all
    def write_all(self, dataset: List[Any], **kwargs):
        '''
        Write an entire dataset to the CSV file.
        
        :param dataset: List of rows to write.
        :type dataset: List[List[Any]]
        :param kwargs: Additional keyword arguments for csv.writer.
        :type kwargs: dict
        '''

        # Build a CSV writer.
        self.build_writer(**kwargs)

        self.writer.writerows(dataset)

    # * method: get_start_line_num (static)
    @staticmethod
    def get_start_line_num(start_index: int = None, has_header: bool = True) -> int:
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

    # * method: get_end_line_num (static)
    @staticmethod
    def get_end_line_num(end_index: int = None, has_header: bool = True) -> int:
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

    # * method: yield_rows (static)
    @staticmethod
    def yield_rows(
        csv_loader: 'CsvLoader',
        start_line_num: int = 1,
        end_line_num: int = -1,
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        A generator function to yield rows from the CSV file within a specified line number range.

        :param csv_loader: An instance of the CsvLoader class for reading the CSV file.
        :type csv_loader: CsvLoader
        :param start_line_num: The starting line number for reading rows.
        :type start_line_num: int
        :param end_line_num: The non-inclusive ending line number for reading rows.
        :type end_line_num: int
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Read rows one by one.
        while True:
            row, line_num = csv_loader.read_row(**csv_settings)

            # Break the loop if there are no more rows or we reached the end index.
            if line_num == -1 or line_num == end_line_num:
                break

            # Yield the row if it falls within the specified line number range.
            if start_line_num <= line_num < (end_line_num if end_line_num != -1 else float('inf')):
                yield row

    # * method: load_rows (static)
    @staticmethod
    def load_rows(
        csv_file: str,
        is_dict: bool = False,
        start_index: int = None,
        end_index: int = None,
        has_header: bool = True,
        data_factory: Callable = lambda data: data,
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ) -> List[Any]:
        '''
        Load rows from the CSV file.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
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
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        :return: A list of loaded rows.
        :rtype: List[Any]
        '''

        # Raise an error if rows are loaded as dicts with no header.
        if is_dict and not has_header:
            RaiseError.execute(
                a.const.CSV_DICT_NO_HEADER_ID,
                'Cannot load CSV rows as dictionaries when has_header is False.',
                csv_file=csv_file
            )

        # Determine whether to use CsvDictLoader or CsvLoader based on is_dict flag.
        CsvClass = CsvDictLoader if is_dict else CsvLoader

        # Create a CsvLoader instance with the configured settings.
        with CsvClass(
            path=csv_file,
            mode='r',
            encoding=encoding,
            newline=newline
        ) as csv_loader:

            # Load and return all rows from the CSV file if the start and end indices are not specified.
            if start_index is None and end_index is None:
                return [data_factory(row) for row in csv_loader.read_all(**csv_settings)]

            # Specify the start line number.
            start_line_num = CsvLoader.get_start_line_num(
                start_index=start_index,
                has_header=has_header
            )

            # Specify the end line number.
            end_line_num = CsvLoader.get_end_line_num(
                end_index=end_index,
                has_header=has_header
            )

            # Return the list of rows from the generator.
            return [
                data_factory(row) for row in CsvLoader.yield_rows(
                    csv_loader=csv_loader,
                    start_line_num=start_line_num,
                    end_line_num=end_line_num,
                    csv_settings=csv_settings
                )
            ]

    # * method: append_row (static)
    @staticmethod
    def append_row(
        csv_file: str,
        row: List[Any],
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        Append a single row to the CSV file.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param row: A list of values representing the row to append.
        :type row: List[Any]
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Create a CsvLoader instance with append mode.
        with CsvLoader(
            path=csv_file,
            mode='a',
            encoding=encoding,
            newline=newline
        ) as csv_saver:

            # Append the specified row to the CSV file.
            csv_saver.write_row(row, **csv_settings)

    # * method: append_dict_row (static)
    @staticmethod
    def append_dict_row(
        csv_file: str,
        row: Dict[str, Any],
        fieldnames: List[str],
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        Append a single dictionary row to the CSV file.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param row: A dictionary representing the row to append (keys match fieldnames).
        :type row: Dict[str, Any]
        :param fieldnames: List of field names for the CSV DictWriter.
        :type fieldnames: List[str]
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Create a CsvDictLoader instance with append mode.
        with CsvDictLoader(
            path=csv_file,
            mode='a',
            encoding=encoding,
            newline=newline
        ) as csv_saver:

            # Append the specified dictionary row to the CSV file.
            csv_saver.write_row(
                row,
                fieldnames=fieldnames,
                include_header=False,
                **csv_settings
            )

    # * method: save_rows (static)
    @staticmethod
    def save_rows(
        csv_file: str,
        dataset: List[List[Any]],
        mode: str = 'w',
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        Save multiple rows to the CSV file.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param dataset: A list of rows, where each row is a list of values.
        :type dataset: List[List[Any]]
        :param mode: The file mode (default is 'w' for write).
        :type mode: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Create a CsvLoader instance with the specified mode.
        with CsvLoader(
            path=csv_file,
            mode=mode,
            encoding=encoding,
            newline=newline
        ) as csv_saver:

            # Save all rows to the CSV file.
            csv_saver.write_all(dataset, **csv_settings)

    # * method: save_dict_rows (static)
    @staticmethod
    def save_dict_rows(
        csv_file: str,
        dataset: List[Dict[str, Any]],
        fieldnames: List[str],
        mode: str = 'w',
        encoding: str = 'utf-8',
        newline: str = '',
        csv_settings: Dict[str, Any] = {}
    ):
        '''
        Save multiple dictionary rows to the CSV file.

        :param csv_file: The path to the CSV file.
        :type csv_file: str
        :param dataset: A list of dictionary rows (keys match fieldnames).
        :type dataset: List[Dict[str, Any]]
        :param fieldnames: List of field names for the CSV DictWriter.
        :type fieldnames: List[str]
        :param mode: The file mode (default is 'w' for write).
        :type mode: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param newline: The newline parameter for file operations (default is '').
        :type newline: str
        :param csv_settings: Additional CSV settings as a dictionary.
        :type csv_settings: Dict[str, Any]
        '''

        # Determine whether to include the header based on the mode.
        include_header = True if mode == 'w' else False

        # Create a CsvDictLoader instance with the specified mode.
        with CsvDictLoader(
            path=csv_file,
            mode=mode,
            encoding=encoding,
            newline=newline
        ) as csv_saver:

            # Save all dictionary rows to the CSV file.
            csv_saver.write_all(
                dataset,
                fieldnames=fieldnames,
                include_header=include_header,
                **csv_settings
            )

# ** util: csv_dict_loader
class CsvDictLoader(CsvLoader):
    '''
    CSV loader utility specialised for dict-based rows.
    '''

    # * attribute: reader
    reader: csv.DictReader

    # * attribute: writer
    writer: csv.DictWriter

    # * method: build_reader
    def build_reader(self, **kwargs) -> csv.DictReader:
        '''
        Build a CSV DictReader from the opened file.

        :param kwargs: Additional keyword arguments for csv.DictReader.
        :type kwargs: dict
        :return: A CSV DictReader object.
        :rtype: csv.DictReader
        '''

        # Ensure the file is opened.
        if self.file is None:
            RaiseError.execute(
                a.const.CSV_HANDLE_NOT_INITIALIZED_ID,
                'CSV handle not initialized. Use within "with" block.'
            )

        # Ensure the mode is readable.
        if self.mode[0] not in {'r'}:
            RaiseError.execute(
                a.const.CSV_INVALID_READ_MODE_ID,
                f'Cannot read in mode {self.mode!r}',
                mode=self.mode
            )
        
        # Build and set the CSV DictReader.
        self.reader = csv.DictReader(self.file, **kwargs)
    
    # * method: build_writer
    def build_writer(self, fieldnames: List[str], **kwargs) -> csv.DictWriter:
        '''
        Build a CSV DictWriter for the opened file.

        :param kwargs: Additional keyword arguments for csv.DictWriter.
        :type kwargs: dict
        :return: A CSV DictWriter object.
        :rtype: csv.DictWriter
        '''

        # Ensure the file is opened.
        if self.file is None:
            RaiseError.execute(
                a.const.CSV_HANDLE_NOT_INITIALIZED_ID,
                'CSV handle not initialized. Use within "with" block.'
            )

        # Ensure the mode is writable.
        if self.mode[0] not in {'w', 'a'}:
            RaiseError.execute(
                a.const.CSV_INVALID_WRITE_MODE_ID,
                f'Cannot write in mode {self.mode!r}',
                mode=self.mode
            )
        
        # Ensure fieldnames are provided.
        if not fieldnames:
            RaiseError.execute(
                a.const.CSV_FIELDNAMES_REQUIRED_ID,
                'Fieldnames must be provided for DictWriter.'
            )

        # Build and set the CSV DictWriter.
        self.writer = csv.DictWriter(
            self.file, 
            fieldnames,
            **kwargs
        )
    
    # * method: write_row
    def write_row(self, 
        row: Dict[str, Any],
        fieldnames = List[str],
        include_header: bool = True,
        **kwargs
    ):
        '''
        Write a single dict-based row to the CSV file.
        
        :param row: A dict (keys match fieldnames) or list of values.
        :type row: dict
        :param include_header: Write header row before the row.
        :type include_header: bool
        :param fieldnames: List of field names for the CSV DictWriter.
        :type fieldnames: List[str]
        '''

        # Build a CSV DictWriter.
        if not self.writer:
            self.build_writer(fieldnames=fieldnames, **kwargs)

        # Write the header if requested.
        if include_header:
            self.writer.writeheader()

        # Write the row.
        self.writer.writerow(row)

    # * method: write_all
    def write_all(
        self,
        dataset: List[Dict[str, Any]],
        fieldnames: List[str],
        include_header: bool = True,
        **kwargs
    ):
        '''
        Write an entire dataset of dict-based rows to the CSV file.
        
        :param dataset: List of dict-based rows to write.
        :type dataset: List[Dict[str, Any]]
        :param fieldnames: List of field names for the CSV DictWriter.
        :type fieldnames: List[str]
        :param kwargs: Additional keyword arguments for csv.DictWriter.
        :type kwargs: dict
        '''

        # Build a CSV DictWriter.
        self.build_writer(fieldnames=fieldnames, **kwargs)

        # Write the header if requested.
        if include_header:
            self.writer.writeheader()

        # Write all rows.
        self.writer.writerows(dataset)