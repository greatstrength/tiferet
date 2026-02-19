"""Tiferet Logging YAML Repository"""

# *** imports

# ** core
from typing import (
    Tuple,
    List
)

# ** app
from ..interfaces import LoggingService
from ..mappers import (
    LoggingSettingsYamlObject,
    FormatterAggregate,
    FormatterYamlObject,
    HandlerAggregate,
    HandlerYamlObject,
    LoggerAggregate,
    LoggerYamlObject,
    TransferObject
)
from ..utils import Yaml

# *** repos

# ** repo: logging_yaml_repository
class LoggingYamlRepository(LoggingService):
    '''
    YAML-backed repository for logging configurations (formatters, handlers, loggers).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the logging YAML repository.

        :param yaml_file: Path to YAML logging config file
        :type yaml_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]:
        '''
        List all formatter, handler, and logger configurations.

        :return: Tuple of (formatters, handlers, loggers)
        :rtype: Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]
        '''

        # Load the logging data from the yaml configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load the logging settings data.
            data = yaml_file.load(
                data_factory=lambda d: LoggingSettingsYamlObject.from_yaml_data(**d),
                start_node=lambda d: d.get('logging', {})
            )

        # Return the formatters, handlers, and loggers.
        return (
            [f.map() for f in data.formatters.values()],
            [h.map() for h in data.handlers.values()],
            [l.map() for l in data.loggers.values()]
        )

    # * method: save_formatter
    def save_formatter(self, formatter: FormatterAggregate):
        '''
        Save/update a formatter configuration.

        :param formatter: The formatter configuration to save.
        :type formatter: FormatterAggregate
        '''

        # Create formatter data object from the model.
        formatter_data = TransferObject.from_model(
            FormatterYamlObject,
            formatter
        )

        # Save the formatter data to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the formatter data.
            yaml_file.save(
                formatter_data.to_primitive(self.default_role),
                data_path=f'logging.formatters.{formatter.id}'
            )

    # * method: save_handler
    def save_handler(self, handler: HandlerAggregate):
        '''
        Save/update a handler configuration.

        :param handler: The handler configuration to save.
        :type handler: HandlerAggregate
        '''

        # Create handler data object from the model.
        handler_data = TransferObject.from_model(
            HandlerYamlObject,
            handler
        )

        # Save the handler data to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the handler data.
            yaml_file.save(
                handler_data.to_primitive(self.default_role),
                data_path=f'logging.handlers.{handler.id}'
            )

    # * method: save_logger
    def save_logger(self, logger: LoggerAggregate):
        '''
        Save/update a logger configuration.

        :param logger: The logger configuration to save.
        :type logger: LoggerAggregate
        '''

        # Create logger data object from the model.
        logger_data = TransferObject.from_model(
            LoggerYamlObject,
            logger
        )

        # Save the logger data to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the logger data.
            yaml_file.save(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load all formatters data.
            formatter_data = yaml_file.load(
                start_node=lambda d: d.get('logging', {}).get('formatters', {})
            )

        # Pop the formatter data whether it exists or not.
        formatter_data.pop(formatter_id, None)

        # Save the updated formatters data back to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated formatters data.
            yaml_file.save(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load all handlers data.
            handler_data = yaml_file.load(
                start_node=lambda d: d.get('logging', {}).get('handlers', {})
            )

        # Pop the handler data whether it exists or not.
        handler_data.pop(handler_id, None)

        # Save the updated handlers data back to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated handlers data.
            yaml_file.save(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load all loggers data.
            logger_data = yaml_file.load(
                start_node=lambda d: d.get('logging', {}).get('loggers', {})
            )

        # Pop the logger data whether it exists or not.
        logger_data.pop(logger_id, None)

        # Save the updated loggers data back to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated loggers data.
            yaml_file.save(
                logger_data,
                data_path='logging.loggers'
            )
