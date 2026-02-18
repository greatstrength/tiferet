"""Tiferet YAML Utility"""

# *** imports

# ** core
import os
from typing import (
    Any,
    Dict,
    List,
    Callable
)

# ** infra
import yaml

# ** app
from .file import FileLoaderMiddleware
from ..events import RaiseError, a

# *** utils

# ** util: yaml_loader
class YamlLoader(FileLoaderMiddleware):
    '''
    Utility for loading YAML files into the application.
    '''

    # * attribute: cache_data
    cache_data: Dict[str, Any]

    # * method: verify_yaml_file (static)
    @staticmethod
    def verify_yaml_file(yaml_file: str, default_path: str = None) -> str:
        '''
        Verify that the YAML file exists and is a valid YAML file.

        :param yaml_file: The YAML file path to verify.
        :type yaml_file: str
        :param default_path: An optional default path location to search for the YAML file.
        :type default_path: str
        :return: The verified YAML file path.
        :rtype: str
        '''

        # Generate possible paths for the YAML file.
        yaml_files = [yaml_file]
        if default_path:
            yaml_files.append(os.path.join(default_path, yaml_file))

        # Verify the YAML is valid and file exists in one of the possible paths.
        last_exception = None
        for file in yaml_files:
            try:
                # Check if file exists.
                if not os.path.exists(file):
                    RaiseError.execute(
                        a.const.YAML_FILE_NOT_FOUND_ID,
                        f'YAML file {file} does not exist.',
                        path=file
                    )

                # Verify the file is a valid YAML file.
                if not file.endswith('.yaml') and not file.endswith('.yml'):
                    RaiseError.execute(
                        a.const.INVALID_YAML_FILE_ID,
                        f'File {file} is not a valid YAML file.',
                        path=file
                    )

                # Return the verified file path.
                return file

            # Try the next possible path if file not found.
            except Exception as e:
                if hasattr(e, 'error_code') and e.error_code == a.const.YAML_FILE_NOT_FOUND_ID:
                    last_exception = e
                    continue
                # Break on any other exception.
                last_exception = e
                break

            # Break on any other exception.
            except Exception as e:
                last_exception = e
                break

        # Raise an error if no valid YAML file was found.
        RaiseError.execute(
            a.const.YAML_FILE_NOT_FOUND_ID,
            f'Valid YAML file not found at path: {yaml_file}',
            yaml_file=yaml_file,
            exception=str(last_exception) if last_exception else None
        )

    # * method: __enter__
    def __enter__(self):
        '''
        Enter the context manager and open the YAML file.

        :return: The YamlLoader instance.
        :rtype: YamlLoader
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
    
    # * method: verify_file
    def verify_file(self, path: str):
        '''
        Verify that the opened file is a valid YAML file.
        '''

        # Attempt to load the YAML content to verify its validity.
        # Verify that the configuration file is a valid YAML file.
        if not path or (not path.endswith('.yaml') and not path.endswith('.yml')):
            RaiseError.execute(
                a.const.INVALID_YAML_FILE_ID,
                f'File {path} is not a valid YAML file.',
                path=path
            )
        
        super().verify_file(path)

    # * method: load
    def load(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> List[Any] | Dict[str, Any]:
        '''
        Load the YAML file and return its contents as a dictionary.

        :param start_node: A callable to specify the starting node for loading data from the YAML file. Defaults to a lambda that returns the data as is.
        :type start_node: Callable
        :param data_factory: A callable to specify how to create data objects from the loaded YAML data. Defaults to a lambda that returns the data as is.
        :type data_factory: Callable
        :return: The contents of the YAML file as a dictionary.
        :rtype: List[Any] | Dict[str, Any]
        '''

        # Load the YAML file with exception handling.
        try:
            # Load the YAML content from the file.
            yaml_content = yaml.safe_load(self.file)
            
            # Navigate to the start node of the loaded YAML content.
            yaml_content = start_node(yaml_content)

            # Return the YAML content processed by the data factory.
            return data_factory(yaml_content)

        # Handle any exceptions that occur during YAML loading and raise a custom error.
        except Exception as e:
            RaiseError.execute(
                a.const.YAML_FILE_LOAD_ERROR_ID,
                f'An error occurred while loading the YAML file {self.path}: {str(e)}',
                path=self.path,
                exception=str(e)
            )

    # * method: save
    def save(self, data: Dict[str, Any], data_path: str = None):
        '''
        Save a dictionary as a YAML file.

        :param data: The dictionary to save as YAML.
        :type data: Dict[str, Any]
        :param data_path: The path to save the YAML file to. If None, saves to the current file.
        :type data_path: str
        '''

        # Save the YAML data with exception handling.
        try:
            # If a specific path is not provided, save to the current file using the context manager.
            if not data_path:
                yaml.safe_dump(data, self.file)
                return

            # Get the data save path list. Replace any '.' with '/' for path consistency.
            data_path = data_path.replace('.', '/')
            save_path_list = data_path.split('/')

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

        # Handle any exceptions that occur during YAML saving and raise a custom error.
        except Exception as e:
            RaiseError.execute(
                a.const.YAML_FILE_SAVE_ERROR_ID,
                f'An error occurred while saving to the YAML file {self.path}: {str(e)}',
                path=self.path,
                exception=str(e)
            )
