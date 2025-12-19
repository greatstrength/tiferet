"""Tiferet JSON Proxy Settings"""

# *** imports

# ** core
from typing import Any, Callable

# ** app
from ...commands import RaiseError
from ...middleware import Json

# *** classes

# ** class json_file_proxy
class JsonFileProxy(object):
    '''
    A base class for proxies that handle JSON configuration files.
    '''

    # * attribute: json_file
    json_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: indent
    indent: int

    # * attribute: default_role
    default_role: str

    # * method: init
    def __init__(self, json_file: str, encoding: str = 'utf-8', default_role: str = 'to_data.json', indent: int = 4):
        '''
        Initialize the proxy.

        :param config_file: The configuration file.
        :type config_file: str
        '''

        # Verify that the configuration file is a valid JSON file.
        if not json_file or not json_file.endswith('.json'):
            RaiseError.execute(
                'INVALID_JSON_FILE',
                f'File is not a valid JSON file: {json_file}.',
                json_file=json_file
            )

        self.json_file = json_file
        self.encoding = encoding
        self.default_role = default_role
        self.indent = indent

    # * method: load_json
    def load_json(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load data from the JSON configuration file.

        :param start_node: A callable to specify the starting node for loading data from the JSON file. Defaults to a lambda that returns the data as is.
        :type start_node: Callable
        :param data_factory: A callable to specify how to create data objects from the loaded JSON data. Defaults to a lambda that returns the data as is.
        :type data_factory: Callable
        :return: The loaded data.
        :rtype: any
        '''

        # Load the JSON file.
        try:

            # Use the Json middleware to load the JSON file.
            with Json(self.json_file, mode='r', encoding=self.encoding) as json_loader:
                data = json_loader.load_json(start_node=start_node)

            # Process the loaded data using the data factory.
            return data_factory(data)
        
        # Handle any exceptions that occur during loading.
        except Exception as e:
            RaiseError.execute(
                'JSON_FILE_LOAD_ERROR',
                f'An error occurred while loading the JSON file: {self.json_file}, {str(e)}',
                json_file=self.json_file
            )

    # * method: save_json
    def save_json(self, data: Any, data_json_path: str = None, indent: int = None):
        '''
        Save data to the JSON configuration file.

        :param data: The data to save.
        :type data: any
        :param data_json_path: The JSON path within the file where the data should be saved. If None, saves to the root.
        :type data_json_path: str
        :param indent: The number of spaces to use for indentation in the JSON file. If None, uses the default indent.
        :type indent: int
        '''

        # Save the data to the JSON file.
        try:

            # Use the Json middleware to save the JSON file.
            with Json(
                self.json_file,
                mode='w',
                encoding=self.encoding
            ) as json_saver:
                json_saver.save_json(
                    data,
                    data_json_path=data_json_path,
                    indent=indent if indent else self.indent
                )

        # Handle any exceptions that occur during saving.
        except Exception as e:
            RaiseError.execute(
                'JSON_FILE_SAVE_ERROR',
                f'An error occurred while saving to the JSON file {self.json_file}: {str(e)}',
                json_file=self.json_file
            )