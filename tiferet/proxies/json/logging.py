"""Tiferet Logging JSON Proxy"""

# *** imports

# ** core
from typing import (
    List,
    Any,
    Tuple,
    Callable
)

# ** app
from ...commands import RaiseError
from ...data import (
    LoggingSettingsConfigData,
    FormatterConfigData,
    HandlerConfigData,
    LoggerConfigData,
    DataObject
)
from ...contracts import (
    LoggingRepository,
    FormatterContract,
    HandlerContract,
    LoggerContract
)
from .settings import JsonFileProxy

# *** proxies

# ** proxy: logging_json_proxy
class LoggingJsonProxy(LoggingRepository, JsonFileProxy):
    '''
    JSON proxy for logging configurations.
    '''

    # * init
    def __init__(self, logging_config_file: str):
        '''
        Initialize the JSON proxy.

        :param logging_config_file: The JSON file path for the logging configuration.
        :type logging_config_file: str
        '''

        # Set the logging configuration file.
        super().__init__(logging_config_file)

    # * method: load_json
    def load_json(
            self,
            start_node: Callable = lambda data: data,
            data_factory: Callable = lambda data: data
        ) -> Any:
        '''
        Load data from the JSON configuration file.

        :param start_node: The starting node in the JSON file.
        :type start_node: callable
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the JSON file contents using the json config proxy.
        try:
            return super().load_json(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'LOGGING_CONFIG_LOADING_FAILED',
                f'Unable to load logging configuration file {self.json_file}: {e}.',
                json_file=self.json_file,
                exception=str(e)
            )

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all formatter, handler, and logger configurations from the JSON file.

        :return: Lists of formatter, handler, and logger configurations.
        :rtype: Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]
        '''

        # Load the JSON data for formatters, handlers, and loggers.
        data = self.load_json(
            data_factory=lambda data: LoggingSettingsConfigData.from_data(
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

    # * method: save_formatter
    def save_formatter(self, formatter: FormatterContract):
        '''
        Save a formatter configuration to the JSON file.

        :param formatter: The formatter configuration to save.
        :type formatter: FormatterContract
        '''

        # Convert the formatter to LoggingSettingsData.
        formatter_data = DataObject.from_model(
            FormatterConfigData,
            formatter
        )

        # Save the formatter data to the JSON file.
        self.save_json(
            formatter_data.to_primitive(self.default_role),
            data_json_path=f'logging.formatters.{formatter.id}',
        )

    # * method: save_handler
    def save_handler(self, handler: HandlerContract):
        '''
        Save a handler configuration to the JSON file.

        :param handler: The handler configuration to save.
        :type handler: HandlerContract
        '''

        # Convert the handler to LoggingSettingsData.
        handler_data = DataObject.from_model(
            HandlerConfigData,
            handler
        )

        # Save the handler data to the JSON file.
        self.save_json(
            handler_data.to_primitive(self.default_role),
            data_json_path=f'logging.handlers.{handler.id}',
        )

    # * method: save_logger
    def save_logger(self, logger: LoggerContract):
        '''
        Save a logger configuration to the JSON file.

        :param logger: The logger configuration to save.
        :type logger: LoggerContract
        '''

        # Convert the logger to LoggingSettingsData.
        logger_data = DataObject.from_model(
            LoggerConfigData,
            logger
        )

        # Save the logger data to the JSON file.
        self.save_json(
            logger_data.to_primitive(self.default_role),
            data_json_path=f'logging.loggers.{logger.id}',
        )

    # * method: delete_formatter
    def delete_formatter(self, formatter_id: str):
        '''
        Delete a formatter configuration from the JSON file.

        :param formatter_id: The ID of the formatter to delete.
        :type formatter_id: str
        '''

        # Get the raw data for the configured formatters.
        formatter_data = self.load_json(
            start_node=lambda data: data.get('logging').get('formatters', {})
        )

        # Pop the formatter regardless of its existence.
        formatter_data.pop(formatter_id, None)

        # Save the updated formatter data back to the JSON file.
        self.save_json(
            formatter_data,
            data_json_path='logging.formatters'
        )

    # * method: delete_handler
    def delete_handler(self, handler_id: str):
        '''
        Delete a handler configuration from the JSON file.

        :param handler_id: The ID of the handler to delete.
        :type handler_id: str
        '''

        # Get the raw data for the configured handlers.
        handler_data = self.load_json(
            start_node=lambda data: data.get('logging').get('handlers', {})
        )

        # Pop the handler regardless of its existence.
        handler_data.pop(handler_id, None)

        # Save the updated handler data back to the JSON file.
        self.save_json(
            handler_data,
            data_json_path='logging.handlers'
        )

    # * method: delete_logger
    def delete_logger(self, logger_id: str):
        '''
        Delete a logger configuration from the JSON file.

        :param logger_id: The ID of the logger to delete.
        :type logger_id: str
        '''

        # Get the raw data for the configured loggers.
        logger_data = self.load_json(
            start_node=lambda data: data.get('logging').get('loggers', {})
        )

        # Pop the logger regardless of its existence.
        logger_data.pop(logger_id, None)

        # Save the updated logger data back to the JSON file.
        self.save_json(
            logger_data,
            data_json_path='logging.loggers'
        )