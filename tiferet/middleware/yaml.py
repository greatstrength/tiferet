"""Tiferet YAML Middleware"""

# *** imports
import yaml
from typing import (
    Any,
    Dict,
    List,
    Callable
)

# ** app
from .file import FileLoaderMiddleware

# *** middleware

#* middleware: yaml_loader
class YamlLoaderMiddleware(FileLoaderMiddleware):
    '''
    Middleware for loading YAML files into the application.
    '''

    # * attribute: cache_data
    cache_data: Dict[str, Any]

    # * method: __enter__
    def __enter__(self):
        '''
        Enter the context manager and open the YAML file.

        :return: The YamlLoaderMiddleware instance.
        :rtype: YamlLoaderMiddleware
        '''
        
        # If the mode is 'w' or 'wb', read the existing YAML content to cache it before writing.
        if self.mode in ['w', 'wb']:
            with open(self.path, 'r', encoding=self.encoding) as f:
                self.cache_data = yaml.safe_load(f) or {}
        else:
            self.cache_data = None

        # Open the file using the parent class's context manager.
        return super().__enter__()
    
    # * method: __exit__
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Exit the context manager and close the YAML file.

        :param exc_type: The type of exception raised (if any).
        :type exc_type: type
        :param exc_value: The value of the exception raised (if any).
        :type exc_value: Exception
        :param traceback: The traceback of the exception raised (if any).
        :type traceback: traceback
        '''

        # Clear the cache data when exiting the context.
        self.cache_data = None

        # Close the file using the parent class's context manager.
        return super().__exit__(exc_type, exc_value, traceback)

    # * method: load_yaml
    def load_yaml(self, start_node: Callable = lambda data: data) -> List[Any] | Dict[str, Any]:
        '''
        Load the YAML file and return its contents as a dictionary.

        :return: The contents of the YAML file as a dictionary.
        :rtype: List[Any] | Dict[str, Any]
        '''

        # Load the YAML content from the file.
        yaml_content = yaml.safe_load(self.file)
        
        # Return the loaded YAML content as a dictionary.
        return start_node(yaml_content)
    
    # * method: save_yaml
    def save_yaml(self, data: Dict[str, Any], data_yaml_path: str = None):
        '''
        Save a dictionary as a YAML file.

        :param data: The dictionary to save as YAML.
        :type data: Dict[str, Any]
        :param data_yaml_path: The path to save the YAML file to. If None, saves to the current file.
        :type data_yaml_path: str
        '''

        # If a specific path is not provided, save to the current file using the context manager.
        if not data_yaml_path:
            yaml.safe_dump(data, self.file)
            return

        # Get the data save path list.
        save_path_list = data_yaml_path.split('/')

        # Update the yaml data.
        new_yaml_data = None
        for fragment in save_path_list[:-1]:

            # If the new yaml data exists, update it.
            try:
                new_yaml_data = new_yaml_data[fragment]

            # If the new yaml data does not exist, create it from the yaml data.
            except TypeError:
                try:
                    new_yaml_data = self.cache_data[fragment]
                    continue  
            
                # If the fragment does not exist, create it.
                except KeyError:
                    new_yaml_data = self.cache_data[fragment] = {}

            # If the fragment does not exist, create it.
            except KeyError: 
                new_yaml_data[fragment] = {}
                new_yaml_data = new_yaml_data[fragment]

        # Update the yaml data.
        try:
            new_yaml_data[save_path_list[-1]] = data
        # if there is a type error because the new yaml data is None, update the yaml data directly.
        except TypeError:
            self.cache_data[save_path_list[-1]] = data

        # Save the updated yaml data.
        yaml.safe_dump(self.cache_data, self.file)