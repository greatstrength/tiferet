"""Tiferet YAML Proxy Settings"""

# *** imports

# ** core
import os
from typing import Dict, Any, Callable

# ** app
from ...commands import raise_error
from ...middleware import Yaml

# *** classes

# ** class yaml_file_proxy
class YamlFileProxy(object):
    '''
    A base class for proxies that handle YAML configuration files.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_path
    default_path: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * method: init
    def __init__(self, yaml_file: str, default_path: str = None, encoding: str = 'utf-8', default_role: str = 'to_data.yaml'):
        '''
        Initialize the proxy.

        :param yaml_file: The YAML configuration file path.
        :type yaml_file: str
        :param default_path: An optional default path location of the YAML file.
        :type default_path: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param default_role: The default role for data serialization/deserialization.
        :type default_role: str
        '''

        # Set the attributes.
        self.yaml_file = self.verify_yaml_file(yaml_file, default_path=default_path)
        self.default_path = default_path
        self.encoding = encoding
        self.default_role = default_role

    # * method: verify_yaml_file
    @staticmethod
    def verify_yaml_file(yaml_file: str, default_path: str = None) -> str:
        '''
        Verify that the YAML file exists and is a valid YAML file.

        :return: The verified YAML file path.
        :rtype: str
        '''

        # Generate possible paths for the YAML file.
        yaml_files = [
            yaml_file
        ]
        if default_path:
            yaml_files.append(
                os.path.join(default_path, yaml_file)
            )

        # Verify the YAML is valid and file exists in one of the possible paths.
        has_error = True
        for file in yaml_files:
            try:

                # Verify the file exists and is a valid YAML file.
                Yaml.verify_file(file)
                return file

            # Try the next possible path if file not found.
            except FileNotFoundError:
                continue

            # Break on any other exception (like invalid YAML).
            except Exception:
                break

        # Raise an error if no valid YAML file was found or is invalid.
        if has_error:
            raise_error.execute(
                'INVALID_YAML_FILE',
                f'Valid YAML file not found at path: {yaml_file}.',
                yaml_file
            )

    # * method: load_yaml
    def load_yaml(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.

        :param start_node: A callable to specify the starting node for loading data from the YAML file. Defaults to a lambda that returns the data as is.
        :type start_node: Callable
        :param data_factory: A callable to specify how to create data objects from the loaded YAML data. Defaults to a lambda that returns the data as is.
        :type data_factory: Callable
        :return: The loaded data.
        :rtype: any
        '''

        # Load the YAML file using the yaml client.
        try:

            # Load the YAML data using the provided start node.
            with Yaml(self.yaml_file, encoding=self.encoding) as yml_r:
                yaml_data = yml_r.load_yaml(start_node=start_node)

            # Return the loaded YAML data after processing it with the data factory.
            return data_factory(yaml_data)

        # Handle any exceptions that occur during YAML loading and raise a custom error.
        except Exception as e:
            raise_error.execute(
                'YAML_FILE_LOAD_ERROR',
                f'An error occurred while loading the YAML file {self.yaml_file}: {str(e)}',
                self.yaml_file,
                str(e)
            )

    # * method: save_yaml
    def save_yaml(self, data: Dict[str, Any], data_yaml_path: str = None):
        '''
        Save data to the YAML configuration file.

        :param data: The data to save to the YAML file.
        :type data: Dict[str, Any]
        :param data_yaml_path: The path within the YAML file where the data should be saved. If None, saves to the root of the YAML file.
        :type data_yaml_path: str
        '''

        # Save the YAML data using the yaml client.
        try:
            with Yaml(
                self.yaml_file,
                mode='w',
                encoding=self.encoding
            ) as yaml_saver:
                yaml_saver.save_yaml(data=data, data_yaml_path=data_yaml_path)

        # Handle any exceptions that occur during YAML saving and raise a custom error.
        except Exception as e:
            raise_error.execute(
                'YAML_FILE_SAVE_ERROR',
                f'An error occurred while saving to the YAML file {self.yaml_file}: {str(e)}',
                self.yaml_file,
                str(e)
            )