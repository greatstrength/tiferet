"""Tiferet CSV Middleware"""

# *** imports
import csv
from _csv import Reader, Writer
from typing import (
    List,
    Dict,
    Tuple,
    Any,
    Optional
)

# ** app
from .file import FileLoaderMiddleware


# *** middleware

# * middleware: csv_loader_middleware
class CsvLoaderMiddleware(FileLoaderMiddleware):
    '''
    CSV-specific middleware built on top of FileLoaderMiddleware.
    Supports list-based rows (csv.reader / csv.writer) **and**
    dict-based rows (csv.DictReader / csv.DictWriter) with configurable
    delimiter, newline handling and optional field-names.
    '''

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
            raise ValueError(f'Invalid mode: {mode!r}. CSV supports: {", ".join(sorted(valid_modes))}')

    # * method: build_reader
    def build_reader(self, **kwargs) -> Reader:
        '''
        Build a CSV reader list from the opened file.

        :param kwargs: Additional keyword arguments for csv.reader.
        :type kwargs: dict
        :return: A CSV reader object.
        :rtype: Reader
        '''

        # Ensure the file is opened.
        if self.file is None:
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        # Ensure the mode is readable.
        if self.mode[0] not in {'r'}:
            raise RuntimeError(f'Cannot read in mode {self.mode!r}')
        
        # Else build a standard CSV reader.
        return csv.reader(self.file, **kwargs)

    # * method: build_writer
    def build_writer(self, **kwargs) -> Writer:
        '''
        Build a CSV writer (list or dict) for the opened file.

        :param kwargs: Additional keyword arguments for csv.writer.
        :type kwargs: dict
        :return: A CSV writer object.
        :rtype: Writer
        '''

        # Ensure the file is opened.
        if self.file is None:
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        # Ensure the mode is writable.
        if self.mode[0] not in {'w', 'a'}:
            raise RuntimeError(f'Cannot write in mode {self.mode!r}')

        # Build and return a standard CSV writer.
        return csv.writer(self.file, **kwargs)
    
    # * method: read_row
    def read_row(self, **kwargs) -> Tuple[List[Any], int]:
        '''
        Read a single row from the CSV file as a list with its line number.

        :param kwargs: Additional keyword arguments for csv.reader.
        :type kwargs: dict
        :return: A single row from the CSV file.
        :rtype: List[Any]
        '''
        
        # Build a CSV reader.
        reader = self.build_reader(**kwargs)

        # Read and return a single row.
        return next(reader), reader.line_num
    
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
        reader = self.build_reader(**kwargs)

        # Read and return all rows.
        return list(reader)

    # * method: write_row
    def write_row(self, row: List[Any], **kwargs):
        '''
        Write a single row to the CSV file.
        
        :param row: A dict (keys match fieldnames) or list of values.
        :type row: dict | list
        :param include_header: Write header row before the row (DictWriter only).
        :type include_header: bool
        '''

        # Build a CSV writer.
        writer = self.build_writer(**kwargs)

        # Write the row.
        writer.writerow(row)

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
        writer = self.build_writer(**kwargs)

        writer.writerows(dataset)

# ** middleware: csv_list_loader
class CsvDictLoaderMiddleware(CsvLoaderMiddleware):
    '''
    CSV loader middleware specialised for list-based rows.
    '''

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
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        # Ensure the mode is readable.
        if self.mode[0] not in {'r'}:
            raise RuntimeError(f'Cannot read in mode {self.mode!r}')
        
        # Build and return a CSV DictReader.
        return csv.DictReader(self.file, **kwargs)
    
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
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        # Ensure the mode is writable.
        if self.mode[0] not in {'w', 'a'}:
            raise RuntimeError(f'Cannot write in mode {self.mode!r}')
        
        # Ensure fieldnames are provided.
        if not fieldnames:
            raise ValueError('Fieldnames must be provided for DictWriter.')

        # Build and return a CSV DictWriter.
        return csv.DictWriter(
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
        writer = self.build_writer(fieldnames=fieldnames, **kwargs)

        # Write the header if requested.
        if include_header:
            writer.writeheader()

        # Write the row.
        writer.writerow(row)

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
        writer = self.build_writer(fieldnames=fieldnames, **kwargs)

        # Write the header if requested.
        if include_header:
            writer.writeheader()

        # Write all rows.
        writer.writerows(dataset)