"""Tiferet CSV Loader Middleware"""

# *** imports
import csv
from typing import List, Dict, Any, Optional

# ** app
from .file import FileLoaderMiddleware   # <-- the parent you posted


# *** middleware

# * middleware: csv_loader_middleware
class CsvLoaderMiddleware(FileLoaderMiddleware):
    '''
    CSV-specific middleware built on top of FileLoaderMiddleware.
    Supports list-based rows (csv.reader / csv.writer) **and**
    dict-based rows (csv.DictReader / csv.DictWriter) with configurable
    delimiter, newline handling and optional field-names.
    '''

    # * attribute: delimiter
    delimiter: str

    # * attribute: newline
    newline: str

    # * attribute: use_dict
    use_dict: bool

    # * attribute: fieldnames
    fieldnames: Optional[List[str]]

    # * init
    def __init__(
        self,
        path: str,
        mode: str = 'r',
        encoding: str = 'utf-8',
        delimiter: str = ',',
        newline: str = '',
        use_dict: bool = False,
        fieldnames: Optional[List[str]] = None,
    ):
        '''
        Initialise the CSV loader.

        All file-related validation is performed by the parent
        FileLoaderMiddleware – only CSV options are added here.

        :param path: Path to the CSV file.
        :type path: str
        :param mode: 'r' (read) or 'w' (write).
        :type mode: str
        :param encoding: File encoding (default utf-8).
        :type encoding: str
        :param delimiter: CSV field delimiter.
        :type delimiter: str
        :param newline: Newline handling ('' lets csv manage it).
        :type newline: str
        :param use_dict: Use DictReader / DictWriter instead of list rows.
        :type use_dict: bool
        :param fieldnames: Required for DictWriter; optional for DictReader.
        :type fieldnames: Optional[List[str]]
        '''

        # Let the parent validate path / mode / encoding.
        super().__init__(path=path, mode=mode, encoding=encoding)

        # CSV-specific attributes
        self.delimiter = delimiter
        self.newline = newline
        self.use_dict = use_dict
        self.fieldnames = fieldnames

        # DictWriter needs fieldnames up-front.
        if mode == 'w' and use_dict and not fieldnames:
            raise ValueError('fieldnames must be supplied for DictWriter.')

        # CSV handle will be created in __enter__.
        self.file = None

    # * method: verify_mode
    def verify_mode(self, mode: str):
        '''
        Verify the file mode is compatible with the csv module.
        
        :param mode: The file mode.
        :type mode: str
        '''

        # Valid CSV modes.
        valid_modes = {'r', 'w', 'a', 'r+', 'w+', 'a+'}
        if mode not in valid_modes:
            raise ValueError(
                f'Invalid mode: {mode!r}. '
                f'CSV supports: {", ".join(sorted(valid_modes))}'
            )

    # * method: open_file
    def open_file(self):
        '''
        Open the underlying file **with CSV newline handling**.
        Overrides the parent so that newline=self.newline is passed.
        '''

        # Ensure the file is not already open.
        if self.file is not None:
            raise RuntimeError(f'File already open: {self.path}')

        # Open the file with CSV-specific newline handling.
        self.file = open(
            self.path,
            mode=self.mode,
            encoding=self.encoding,
            newline=self.newline,
        )

    # * method: build_reader
    def build_reader(self):
        '''
        Build a CSV reader (list or dict) from the opened file.
        '''

        # If using DictReader, pass fieldnames if provided.
        if self.use_dict:
            self.file = csv.DictReader(
                self.file,
                fieldnames=self.fieldnames,
                delimiter=self.delimiter,
            )

        # Else build a standard CSV reader.
        else:
            self.file = csv.reader(self.file, delimiter=self.delimiter)

    # * method: build_writer
    def build_writer(self):
        '''
        Build a CSV writer (list or dict) for the opened file.
        '''

        # If using DictWriter, pass fieldnames and write header.
        if self.use_dict:
            self.file = csv.DictWriter(
                self.file,
                fieldnames=self.fieldnames,   # type: ignore[arg-type]
                delimiter=self.delimiter,
            )

            # Write header row automatically for DictWriter.
            self.file.writeheader()
        
        # Else build a standard CSV writer.
        else:
            self.file = csv.writer(self.file, delimiter=self.delimiter)

    # * method: __enter__
    def __enter__(self):
        '''
        Open the file, create the appropriate CSV handle and return self.
        The consumer uses instance.csv_handle (reader or writer).
        '''

        # Open the file (parent logic).
        self.open_file()

        # Build the CSV reader if the mode is read.
        if self.mode[0] == 'r':
            self.build_reader()

        # Build the CSV writer if the mode is write/append.
        else:
            self.build_writer()

        # Return self for use within the context.
        return self

    # * method: __exit__
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Close the file (parent logic) and clear the CSV handle.
        '''

        # Clear the CSV handle.
        self.close_file()

    # * method: save_row
    def save_row(self, row: List[Any] | Dict[str, Any], include_header: bool = False):
        '''
        Write a single row to the CSV file.
        
        :param row: A dict (keys match fieldnames) or list of values.
        :type row: dict | list
        :param include_header: Write header row before the row (DictWriter only).
        :type include_header: bool
        '''
        if self.file is None:
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        if self.mode[0] not in {'w', 'a'}:
            raise RuntimeError(f'Cannot write in mode {self.mode!r}')

        self.file.writerow(row)

    # * method: save_all
    def save_all(self, dataset: List[dict] | List[list], include_header: bool = True):
        '''
        Write an entire dataset to the CSV file.
        
        :param dataset: List of rows to write.
        :type dataset: List[dict] | List[list]
        :param include_header: Write header row (DictWriter only).
        :type include_header: bool
        '''
        if self.file is None:
            raise RuntimeError('CSV handle not initialized. Use within "with" block.')

        if self.mode[0] not in {'w', 'a'}:
            raise RuntimeError(f'Cannot write in mode {self.mode!r}')

        if not dataset:
            return

        # Write header only if file is empty and requested
        if self.use_dict and include_header and self.fieldnames:
            if self.file.writer.csvfile.tell() == 0:   # type: ignore[attr-defined]
                self.file.writeheader()

        self.file.writerows(dataset)