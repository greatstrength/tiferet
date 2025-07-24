# *** imports

# ** core
from typing import List, Tuple

# ** app
from .core import *
from ...data.logging import LoggingSettingsData
from ...contracts.logging import (
    LoggingRepository,
    FormatterContract,
    HandlerContract,
    LoggerContract
)

# *** proxies

# ** proxy: logging_yaml_proxy
class LoggingYamlProxy(LoggingRepository, YamlConfigurationProxy):
    '''
    YAML proxy for logging configurations.
    '''

    # * init
    def __init__(self, logging_config_file: str):
        '''
        Initialize the YAML proxy.

        :param logging_config_file: The YAML file path for the logging configuration.
        :type logging_config_file: str
        '''

        # Set the logging configuration file.
        super().__init__(logging_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.

        :param start_node: The starting node in the YAML file.
        :type start_node: callable
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'LOGGING_CONFIG_LOADING_FAILED',
                f'Unable to load logging configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
            )

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all formatter, handler, and logger configurations from the YAML file.

        :return: Lists of formatter, handler, and logger configurations.
        :rtype: Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]
        '''

        # Load the YAML data for formatters, handlers, and loggers.
        data = self.load_yaml(
            create_data=lambda data: LoggingSettingsData.from_yaml_data(
                **data
            ),
            start_node=lambda data: data.get('logging', {})
        )

        # Ensure the loaded data is in the expected format.
        return (
            [formatter.map() for formatter in data.formatters.values()],
            [handler.map() for handler in data.handlers.values()],
            [logger.map() for logger in data.loggers.values()]
        )
