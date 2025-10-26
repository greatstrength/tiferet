"""Tiferet JSON Middleware"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any,
    Callable
)
import json

# ** app
from .file import FileLoaderMiddleware

# *** middleware

#* middleware: json_loader
class JsonLoaderMiddleware(FileLoaderMiddleware):
    '''
    Middleware for loading JSON files into the application.
    '''

    # * attribute: cache_data
    cache_data: Dict[str, Any]

    # * method: __enter__
    def __enter__(self):
        '''
        Enter the context manager and open the JSON file.

        :return: The JsonLoaderMiddleware instance.
        :rtype: JsonLoaderMiddleware
        '''
        
        # If the mode is 'w' or 'wb', read the existing JSON content to cache it before writing.
        if self.mode in ['w', 'wb']:
            with open(self.path, 'r', encoding=self.encoding) as f:
                self.cache_data = json.load(f) or {}
        else:
            self.cache_data = None

        # Open the file using the parent class's context manager.
        return super().__enter__()
    
    # * method: __exit__
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Exit the context manager and close the JSON file.

        :param exc_type: The type of exception raised (if any).
        :type exc_type: type
        :param exc_value: The value of the exception raised (if any).
        :type exc_value: Exception
        :param traceback: The traceback of the exception raised (if any).
        :type traceback: traceback
        '''

        # Clear the cache data when exiting the context.
        self.cache_data = None

        # Call the parent class's __exit__ method to ensure proper cleanup.
        return super().__exit__(exc_type, exc_value, traceback)

    # * method: load_json
    def load_json(self, start_node: Callable = lambda data: data) -> List[Any] | Dict[str, Any]:
        '''
        Load data from the JSON configuration file.

        :param start_node: A callable to specify the starting node for loading data from the JSON file. Defaults to a lambda that returns the data as is.
        :type start_node: Callable
        '''

        # Load the JSON content from the file.
        json_content = json.load(self.file)

        # Process the JSON content using the provided start node.
        return start_node(json_content)
    
    # * method: parse_json_path
    def parse_json_path(self, path: str) -> List[str | int]:
        '''
        Parse a JSON path into a list of keys and indices.

        :param path: The JSON path to parse (e.g., "key1.key2[0].key3").
        :type path: str
        :return: A list of keys and indices representing the path.
        :rtype: List[str | int]
        '''

        # Split the path into parts and handle array indices.
        parts = []
        for part in path.split('.'):
            if part.endswith(']'):
                # Handle array index
                array_part, index_part = part[:-1].split('[')
                parts.append(array_part)
                parts.append(int(index_part))
            else:
                parts.append(part)
        
        return parts
    
    # * method: save_json
    def save_json(self, data: Dict[str, Any], data_json_path: str = None, indent: int = 4):
        '''
        Save data to the JSON configuration file.

        :param data: The data to save to the JSON file.
        :type data: Dict[str, Any]
        :param data_json_path: The path within the JSON file where the data should be saved. If None, saves to the root of the JSON file.
        :type data_json_path: str
        :param indent: The number of spaces to use for indentation in the JSON file. Defaults to 4.
        :type indent: int
        '''

        # Save the JSON data to the file with the specified indentation if no specific path is provided. 
        if not data_json_path:
            json.dump(data, self.file, indent=indent)
            return

        # Get the data save path list and navigate to the correct location in the JSON structure to save the data.
        save_path_list = self.parse_json_path(data_json_path)

        # Update the JSON data at the specified path.
        current_data = self.cache_data
        for part in save_path_list[:-1]:
            if isinstance(part, int):
                # Handle list index
                while len(current_data) <= part:
                    current_data.append({})
                current_data = current_data[part]
            else:
                # Handle dictionary key
                if part not in current_data:
                    current_data[part] = {}
                current_data = current_data[part]

        # Set the final value at the specified path.
        final_part = save_path_list[-1]
        if isinstance(final_part, int):
            # Handle list index for the final part
            while len(current_data) <= final_part:
                current_data.append({})
            current_data[final_part] = data
        else:
            # Handle dictionary key for the final part
            current_data[final_part] = data

        # Save the updated JSON data to the file with the specified indentation.
        json.dump(self.cache_data, self.file, indent=indent)