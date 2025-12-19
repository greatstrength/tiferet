"""Tiferet Error YAML Proxy"""

# *** imports

# ** core
from typing import (
    Any,
    List,
    Dict,
    Callable
)

# ** app
from ...commands import RaiseError
from ...data import DataObject, ErrorConfigData
from ...contracts import ErrorContract, ErrorRepository
from .settings import YamlFileProxy

# *** proxies

# ** proxy: yaml_proxy
class ErrorYamlProxy(ErrorRepository, YamlFileProxy):
    '''
    The YAML proxy for the error repository
    '''

    # * method: init
    def __init__(self, error_config_file: str):
        '''
        Initialize the yaml proxy.

        :param error_config_file: The error configuration file.
        :type error_config_file: str
        '''

        # Set the base path.
        super().__init__(error_config_file)

    # * method: load_yaml
    def load_yaml(
            self,
            start_node: Callable = lambda data: data,
            data_factory: Callable = lambda data: data
        ) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: Callable
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: Callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'ERROR_CONFIG_LOADING_FAILED',
                f'Unable to load error configuration file {self.yaml_file}: {e}.',
                yaml_file=self.yaml_file,
                exception=str(e)
            )

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.
        
        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Load the error data from the yaml configuration file.
        error = self.get(id)

        # Return whether the error exists.
        return error is not None

    # * method: get
    def get(self, id: str) -> ErrorContract:
        '''
        Get the error.

        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: ErrorContract
        '''

        # Load the error data from the yaml configuration file.
        error_data = self.load_yaml(
            start_node=lambda data: data.get('errors').get(id)
        )

        # If no data is found, return None.
        if not error_data:
            return None
        
        # Map the error data to the error object and return it.
        return DataObject.from_data(
            ErrorConfigData,
            id=id,
            **error_data
        ).map()

    # * method: list
    def list(self) -> List[ErrorContract]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[ErrorContract]
        '''

        # Load the error data from the yaml configuration file.
        errors: Dict[str, ErrorConfigData] = self.load_yaml(
            data_factory=lambda data: {
                id: DataObject.from_data(
                    ErrorConfigData,
                    id=id, 
                    **error_data
                ) for id, error_data in data.items()
            },
            start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [data.map() for data in errors.values()]

    # * method: save
    def save(self, error: ErrorContract):
        '''
        Save the error.

        :param error: The error.
        :type error: ErrorContract
        '''

        # Create updated error data.
        error_data = DataObject.from_model(
            ErrorConfigData, 
            error
        )

        # Update the error data.
        self.save_yaml(
            data=error_data.to_primitive(self.default_role),
            data_yaml_path=f'errors/{error.id}',
        )

    # * method: delete
    def delete(self, id: str):
        '''
        Delete the error.

        :param id: The error id.
        :type id: str
        '''

        # Retrieve the errors data from the yaml file.
        errors_data = self.load_yaml(
            start_node=lambda data: data.get('errors', {})
        )

        # Pop the error data whether it exists or not.
        errors_data.pop(id, None)

        # Save the updated errors data back to the yaml file.
        self.save_yaml(
            data=errors_data,
            data_yaml_path='errors'
        )