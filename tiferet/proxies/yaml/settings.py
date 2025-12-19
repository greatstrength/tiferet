"""Tiferet YAML Proxy Settings"""

# *** imports

# ** core
from typing import Dict, Any, Callable

# ** app
from ...commands import RaiseError
from ...middleware import Yaml

# *** classes

# ** class yaml_file_proxy
class YamlFileProxy(object):
    '''
    A base class for proxies that handle YAML configuration files.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * method: init
    def __init__(self, yaml_file: str, encoding: str = 'utf-8', default_role: str = 'to_data.yaml'):
        '''
        Initialize the proxy.

        :param config_file: The configuration file.
        :type config_file: str
        '''

        # Verify that the configuration file is a valid YAML file.
        if not yaml_file or (not yaml_file.endswith('.yaml') and not yaml_file.endswith('.yml')):
            RaiseError.execute(
                'INVALID_YAML_FILE',
                f'File {yaml_file} is not a valid YAML file.',
                yaml_file=yaml_file
            )

        self.yaml_file = yaml_file
        self.encoding = encoding
        self.default_role = default_role

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
            RaiseError.execute(
                'YAML_FILE_LOAD_ERROR',
                f'An error occurred while loading the YAML file {self.yaml_file}: {str(e)}',
                yaml_file=self.yaml_file,
                exception=str(e)
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
            ) as yml_w:
                yml_w.save_yaml(data=data, data_yaml_path=data_yaml_path)

        # Handle any exceptions that occur during YAML saving and raise a custom error.
        except Exception as e:
            RaiseError.execute(
                'YAML_FILE_SAVE_ERROR',
                f'An error occurred while saving to the YAML file {self.yaml_file}: {str(e)}',
                yaml_file=self.yaml_file,
                exception=str(e)
            )