"""Tiferet Logging Configuration Repository"""

# *** imports

# ** core
from typing import (
    Tuple,
    List
)

# ** app
from ...contracts import (
    FormatterContract,
    HandlerContract,
    LoggerContract,
    LoggingRepository
)
from ...data import (
    LoggingSettingsConfigData,
    FormatterConfigData,
    HandlerConfigData,
    LoggerConfigData,
    DataObject
)
from .settings import ConfigurationFileRepository

# *** repositories

# ** repo: logging_configuration_repository
class LoggingConfigurationRepository(LoggingRepository, ConfigurationFileRepository):
    '''
    YAML-backed repository for logging configurations (formatters, handlers, loggers).
    '''

    # * attribute: logging_config_file
    logging_config_file: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, logging_config_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the logging configuration repository.

        :param logging_config_file: Path to YAML logging config file
        :type logging_config_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.logging_config_file = logging_config_file
        self.encoding = encoding

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all formatter, handler, and logger configurations.

        :return: Tuple of (formatters, handlers, loggers)
        :rtype: Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]
        '''

        # Load the logging data from the yaml configuration file.
        with self.open_config(
            self.logging_config_file,
            mode='r'
        ) as config_file:

            # Load the logging settings data.
            data = config_file.load(
                data_factory=lambda d: LoggingSettingsConfigData.from_yaml_data(**d),
                start_node=lambda d: d.get('logging', {})
            )

        # Return the formatters, handlers, and loggers.
        return (
            [f.map() for f in data.formatters.values()],
            [h.map() for h in data.handlers.values()],
            [l.map() for l in data.loggers.values()]
        )

    # * method: save_formatter
    def save_formatter(self, formatter: FormatterContract):
        '''
        Save/update a formatter configuration.

        :param formatter: The formatter configuration to save.
        :type formatter: FormatterContract
        '''

        # Create formatter data object from the model.
        formatter_data = DataObject.from_model(
            FormatterConfigData,
            formatter
        )

        # Save the formatter data to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the formatter data.
            config_file.save(
                formatter_data.to_primitive(self.default_role),
                data_path=f'logging.formatters.{formatter.id}'
            )

    # * method: save_handler
    def save_handler(self, handler: HandlerContract):
        '''
        Save/update a handler configuration.

        :param handler: The handler configuration to save.
        :type handler: HandlerContract
        '''

        # Create handler data object from the model.
        handler_data = DataObject.from_model(
            HandlerConfigData,
            handler
        )

        # Save the handler data to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the handler data.
            config_file.save(
                handler_data.to_primitive(self.default_role),
                data_path=f'logging.handlers.{handler.id}'
            )

    # * method: save_logger
    def save_logger(self, logger: LoggerContract):
        '''
        Save/update a logger configuration.

        :param logger: The logger configuration to save.
        :type logger: LoggerContract
        '''

        # Create logger data object from the model.
        logger_data = DataObject.from_model(
            LoggerConfigData,
            logger
        )

        # Save the logger data to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the logger data.
            config_file.save(
                logger_data.to_primitive(self.default_role),
                data_path=f'logging.loggers.{logger.id}'
            )

    # * method: delete_formatter
    def delete_formatter(self, formatter_id: str):
        '''
        Delete a formatter by ID (idempotent).

        :param formatter_id: The ID of the formatter to delete.
        :type formatter_id: str
        '''

        # Retrieve the formatters data from the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='r'
        ) as config_file:

            # Load all formatters data.
            formatter_data = config_file.load(
                start_node=lambda d: d.get('logging', {}).get('formatters', {})
            )

        # Pop the formatter data whether it exists or not.
        formatter_data.pop(formatter_id, None)

        # Save the updated formatters data back to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the updated formatters data.
            config_file.save(
                formatter_data,
                data_path='logging.formatters'
            )

    # * method: delete_handler
    def delete_handler(self, handler_id: str):
        '''
        Delete a handler by ID (idempotent).

        :param handler_id: The ID of the handler to delete.
        :type handler_id: str
        '''

        # Retrieve the handlers data from the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='r'
        ) as config_file:

            # Load all handlers data.
            handler_data = config_file.load(
                start_node=lambda d: d.get('logging', {}).get('handlers', {})
            )

        # Pop the handler data whether it exists or not.
        handler_data.pop(handler_id, None)

        # Save the updated handlers data back to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the updated handlers data.
            config_file.save(
                handler_data,
                data_path='logging.handlers'
            )

    # * method: delete_logger
    def delete_logger(self, logger_id: str):
        '''
        Delete a logger by ID (idempotent).

        :param logger_id: The ID of the logger to delete.
        :type logger_id: str
        '''

        # Retrieve the loggers data from the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='r'
        ) as config_file:

            # Load all loggers data.
            logger_data = config_file.load(
                start_node=lambda d: d.get('logging', {}).get('loggers', {})
            )

        # Pop the logger data whether it exists or not.
        logger_data.pop(logger_id, None)

        # Save the updated loggers data back to the yaml file.
        with self.open_config(
            self.logging_config_file,
            mode='w'
        ) as config_file:

            # Save the updated loggers data.
            config_file.save(
                logger_data,
                data_path='logging.loggers'
            )
