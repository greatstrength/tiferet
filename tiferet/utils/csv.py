"""Tiferet Utils Csv"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional

import csv

# ** app
from .file import FileLoader
from ..events import RaiseError, a

# *** utils

# ** util: csv_loader
class CsvLoader(FileLoader):
    '''
    Utility for CSV operations with list-based rows.
    Extends FileLoader for stream lifecycle management.
    '''

    # * attribute: reader
    reader: Optional[csv.reader]

    # * attribute: writer
    writer: Optional[csv.writer]

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'r',
            encoding: str = 'utf-8',
            **kwargs,
        ):
        '''
        Initialize CsvLoader.

        :param path: Path to the CSV file.
        :type path: str | Path
        :param mode: File open mode (e.g., 'r', 'w', 'a', 'r+', 'w+', 'a+').
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

        # Initialize the parent FileLoader with newline='' for CSV compliance.
        super().__init__(path=path, mode=mode, encoding=encoding, newline='', **kwargs)

        # Initialize the reader to None (lazy initialization).
        self.reader = None

        # Initialize the writer to None (lazy initialization).
        self.writer = None

    # * method: __enter__
    def __enter__(self) -> 'CsvLoader':
        '''
        Enter the runtime context and open the file stream.

        :return: The CsvLoader instance with an open file stream.
        :rtype: CsvLoader
        '''

        # Open the file stream.
        self.open_file()

        # Return the loader instance for access to reader/writer methods.
        return self

    # * method: __exit__
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Exit the runtime context, reset reader/writer, and close the file stream.

        :param exc_type: The exception type (if any).
        :param exc_val: The exception value (if any).
        :param exc_tb: The exception traceback (if any).
        :return: False to propagate exceptions.
        :rtype: bool
        '''

        # Reset the reader and writer.
        self.reader = None
        self.writer = None

        # Close the file stream.
        self.close_file()

        # Do not suppress exceptions.
        return False

    # * method: build_reader
    def build_reader(self):
        '''
        Lazily initialize the CSV reader if not already created.

        :raises TiferetError: If the file is not opened in a readable mode.
        '''

        # Return early if the reader is already initialized.
        if self.reader is not None:
            return

        # Verify the file is opened in a readable mode.
        if 'r' not in self.mode and '+' not in self.mode:
            RaiseError.execute(error_code=a.const.CSV_INVALID_READ_MODE_ID)

        # Create the CSV reader from the open file stream.
        self.reader = csv.reader(self.file)

    # * method: build_writer
    def build_writer(self):
        '''
        Lazily initialize the CSV writer if not already created.

        :raises TiferetError: If the file is not opened in a writable mode.
        '''

        # Return early if the writer is already initialized.
        if self.writer is not None:
            return

        # Verify the file is opened in a writable mode.
        if 'w' not in self.mode and 'a' not in self.mode and '+' not in self.mode:
            RaiseError.execute(error_code=a.const.CSV_INVALID_WRITE_MODE_ID)

        # Create the CSV writer from the open file stream.
        self.writer = csv.writer(self.file)

    # * method: read_row
    def read_row(self) -> List[str]:
        '''
        Read the next row from the CSV file.

        :return: The next row as a list of strings, or an empty list at EOF.
        :rtype: List[str]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Attempt to read the next row; return empty list at EOF.
        try:
            return next(self.reader)
        except StopIteration:
            return []

    # * method: read_all
    def read_all(self) -> List[List[str]]:
        '''
        Read all remaining rows from the CSV file.

        :return: A list of rows, each row being a list of strings.
        :rtype: List[List[str]]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Return all remaining rows.
        return list(self.reader)

    # * method: write_row
    def write_row(self, row: List[Any]):
        '''
        Write a single row to the CSV file.

        :param row: A list of values to write as a row.
        :type row: List[Any]
        '''

        # Build the writer if not already initialized.
        self.build_writer()

        # Write the row.
        self.writer.writerow(row)

    # * method: write_all
    def write_all(self, rows: Iterable[List[Any]]):
        '''
        Write multiple rows to the CSV file.

        :param rows: An iterable of rows to write.
        :type rows: Iterable[List[Any]]
        '''

        # Build the writer if not already initialized.
        self.build_writer()

        # Write all rows.
        self.writer.writerows(rows)

    # * method: yield_rows
    def yield_rows(self,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
        ) -> Generator[List[str], None, None]:
        '''
        Yield rows from the CSV file with optional line-range filtering.

        :param start_line: Optional 1-based start line (inclusive).
        :type start_line: Optional[int]
        :param end_line: Optional 1-based end line (inclusive).
        :type end_line: Optional[int]
        :return: A generator yielding rows as lists of strings.
        :rtype: Generator[List[str], None, None]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Yield rows with optional line-range filtering.
        for i, row in enumerate(self.reader, start=1):

            # Skip rows before the start line.
            if start_line is not None and i < start_line:
                continue

            # Stop after the end line.
            if end_line is not None and i > end_line:
                break

            # Yield the row.
            yield row

    # * method: load_rows (static)
    @staticmethod
    def load_rows(csv_file: str | Path, **kwargs) -> List[List[str]]:
        '''
        Load all rows from a CSV file.

        :param csv_file: Path to the CSV file.
        :type csv_file: str | Path
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: A list of rows, each row being a list of strings.
        :rtype: List[List[str]]
        '''

        # Open the CSV file and read all rows.
        with CsvLoader(path=csv_file, mode='r') as loader:
            return loader.read_all()

    # * method: save_rows (static)
    @staticmethod
    def save_rows(csv_file: str | Path,
            dataset: Iterable,
            mode: str = 'w',
            **kwargs,
        ):
        '''
        Save rows to a CSV file. Supports both list and dict datasets.

        :param csv_file: Path to the CSV file.
        :type csv_file: str | Path
        :param dataset: An iterable of rows (lists or dicts) to write.
        :type dataset: Iterable
        :param mode: File open mode (defaults to 'w').
        :type mode: str
        :param kwargs: Additional keyword arguments (fieldnames, include_header).
        :type kwargs: dict
        '''

        # Materialize the dataset to allow type inspection.
        rows = list(dataset)

        # Check if the dataset contains dict rows.
        if rows and isinstance(rows[0], dict):

            # Retrieve fieldnames from kwargs.
            fieldnames = kwargs.get('fieldnames')

            # Raise error if fieldnames are not provided for dict rows.
            if fieldnames is None:
                RaiseError.execute(error_code=a.const.CSV_FIELDNAMES_REQUIRED_ID)

            # Write dict rows using DictWriter.
            with CsvLoader(path=csv_file, mode=mode) as loader:
                writer = csv.DictWriter(loader.file, fieldnames=fieldnames)

                # Write header if requested (default: True).
                if kwargs.get('include_header', True):
                    writer.writeheader()

                # Write all dict rows.
                writer.writerows(rows)

        else:

            # Write list rows using the CsvLoader writer.
            with CsvLoader(path=csv_file, mode=mode) as loader:
                loader.write_all(rows)

    # * method: append_row (static)
    @staticmethod
    def append_row(csv_file: str | Path, row: List[Any]):
        '''
        Append a single row to a CSV file.

        :param csv_file: Path to the CSV file.
        :type csv_file: str | Path
        :param row: A list of values to append.
        :type row: List[Any]
        '''

        # Open the CSV file in append mode and write the row.
        with CsvLoader(path=csv_file, mode='a') as loader:
            loader.write_row(row)


# ** util: csv_dict_loader
class CsvDictLoader(CsvLoader):
    '''
    Utility for CSV operations with dict-based rows.
    Extends CsvLoader for DictReader/DictWriter support.
    '''

    # * attribute: fieldnames
    fieldnames: Optional[List[str]]

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'r',
            encoding: str = 'utf-8',
            fieldnames: Optional[List[str]] = None,
            **kwargs,
        ):
        '''
        Initialize CsvDictLoader.

        :param path: Path to the CSV file.
        :type path: str | Path
        :param mode: File open mode.
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param fieldnames: Optional list of field names for DictReader/DictWriter.
        :type fieldnames: Optional[List[str]]
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

        # Initialize the parent CsvLoader.
        super().__init__(path=path, mode=mode, encoding=encoding, **kwargs)

        # Set the fieldnames for dict operations.
        self.fieldnames = fieldnames

    # * method: build_reader
    def build_reader(self):
        '''
        Lazily initialize the CSV DictReader if not already created.

        :raises TiferetError: If the file is not opened in a readable mode.
        '''

        # Return early if the reader is already initialized.
        if self.reader is not None:
            return

        # Verify the file is opened in a readable mode.
        if 'r' not in self.mode and '+' not in self.mode:
            RaiseError.execute(error_code=a.const.CSV_INVALID_READ_MODE_ID)

        # Create the DictReader from the open file stream.
        self.reader = csv.DictReader(self.file, fieldnames=self.fieldnames)

    # * method: build_writer
    def build_writer(self):
        '''
        Lazily initialize the CSV DictWriter if not already created.

        :raises TiferetError: If the file is not opened in a writable mode or fieldnames are missing.
        '''

        # Return early if the writer is already initialized.
        if self.writer is not None:
            return

        # Verify the file is opened in a writable mode.
        if 'w' not in self.mode and 'a' not in self.mode and '+' not in self.mode:
            RaiseError.execute(error_code=a.const.CSV_INVALID_WRITE_MODE_ID)

        # Verify fieldnames are provided for DictWriter.
        if self.fieldnames is None:
            RaiseError.execute(error_code=a.const.CSV_FIELDNAMES_REQUIRED_ID)

        # Create the DictWriter from the open file stream.
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)

    # * method: read_row
    def read_row(self) -> Dict[str, Any]:
        '''
        Read the next row from the CSV file as a dict.

        :return: The next row as a dict, or an empty dict at EOF.
        :rtype: Dict[str, Any]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Attempt to read the next row; return empty dict at EOF.
        try:
            return next(self.reader)
        except StopIteration:
            return {}

    # * method: read_all
    def read_all(self) -> List[Dict[str, Any]]:
        '''
        Read all remaining rows from the CSV file as dicts.

        :return: A list of rows, each row being a dict.
        :rtype: List[Dict[str, Any]]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Return all remaining rows.
        return list(self.reader)

    # * method: write_row
    def write_row(self, row: Dict[str, Any]):
        '''
        Write a single dict row to the CSV file.

        :param row: A dict of field values to write.
        :type row: Dict[str, Any]
        '''

        # Build the writer if not already initialized.
        self.build_writer()

        # Write the row.
        self.writer.writerow(row)

    # * method: write_all
    def write_all(self, rows: Iterable[Dict[str, Any]]):
        '''
        Write multiple dict rows to the CSV file.

        :param rows: An iterable of dicts to write.
        :type rows: Iterable[Dict[str, Any]]
        '''

        # Build the writer if not already initialized.
        self.build_writer()

        # Write all rows.
        self.writer.writerows(rows)

    # * method: write_header
    def write_header(self):
        '''
        Write the header row to the CSV file.
        '''

        # Build the writer if not already initialized.
        self.build_writer()

        # Write the header row.
        self.writer.writeheader()

    # * method: yield_rows
    def yield_rows(self,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
        ) -> Generator[Dict[str, Any], None, None]:
        '''
        Yield rows from the CSV file as dicts with optional line-range filtering.

        :param start_line: Optional 1-based start line (inclusive, excludes header).
        :type start_line: Optional[int]
        :param end_line: Optional 1-based end line (inclusive, excludes header).
        :type end_line: Optional[int]
        :return: A generator yielding rows as dicts.
        :rtype: Generator[Dict[str, Any], None, None]
        '''

        # Build the reader if not already initialized.
        self.build_reader()

        # Yield rows with optional line-range filtering.
        for i, row in enumerate(self.reader, start=1):

            # Skip rows before the start line.
            if start_line is not None and i < start_line:
                continue

            # Stop after the end line.
            if end_line is not None and i > end_line:
                break

            # Yield the row.
            yield row

    # * method: load_rows (static)
    @staticmethod
    def load_rows(csv_file: str | Path,
            fieldnames: Optional[List[str]] = None,
            **kwargs,
        ) -> List[Dict[str, Any]]:
        '''
        Load all rows from a CSV file as dicts.

        :param csv_file: Path to the CSV file.
        :type csv_file: str | Path
        :param fieldnames: Optional field names (inferred from header if None).
        :type fieldnames: Optional[List[str]]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: A list of dicts representing rows.
        :rtype: List[Dict[str, Any]]
        '''

        # Open the CSV file and read all rows as dicts.
        with CsvDictLoader(path=csv_file, mode='r', fieldnames=fieldnames) as loader:
            return loader.read_all()

    # * method: save_rows (static)
    @staticmethod
    def save_rows(csv_file: str | Path,
            dataset: Iterable[Dict[str, Any]],
            fieldnames: Optional[List[str]] = None,
            mode: str = 'w',
            include_header: bool = True,
            **kwargs,
        ):
        '''
        Save dict rows to a CSV file.

        :param csv_file: Path to the CSV file.
        :type csv_file: str | Path
        :param dataset: An iterable of dicts to write.
        :type dataset: Iterable[Dict[str, Any]]
        :param fieldnames: Field names for the DictWriter (required).
        :type fieldnames: Optional[List[str]]
        :param mode: File open mode (defaults to 'w').
        :type mode: str
        :param include_header: Whether to write the header row (defaults to True).
        :type include_header: bool
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        '''

        # Raise error if fieldnames are not provided.
        if fieldnames is None:
            RaiseError.execute(error_code=a.const.CSV_FIELDNAMES_REQUIRED_ID)

        # Write dict rows with optional header.
        with CsvDictLoader(path=csv_file, mode=mode, fieldnames=fieldnames) as loader:

            # Write header if requested.
            if include_header:
                loader.write_header()

            # Write all dict rows.
            loader.write_all(dataset)
