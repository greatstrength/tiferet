"""Tiferet Logging Mapper Tests"""

# *** imports

# ** app
from ...events import a
from ..settings import TransferObject
from ..logging import (
    FormatterAggregate,
    FormatterYamlObject,
    HandlerAggregate,
    HandlerYamlObject,
    LoggerAggregate,
    LoggerYamlObject,
    LoggingSettingsYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: formatter_aggregate_sample_data
FORMATTER_AGGREGATE_SAMPLE_DATA = {
    'id': 'simple',
    'name': 'Simple Formatter',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

# ** constant: formatter_equality_fields
FORMATTER_EQUALITY_FIELDS = ['id', 'name', 'format', 'datefmt']

# ** constant: handler_aggregate_sample_data
HANDLER_AGGREGATE_SAMPLE_DATA = {
    'id': 'console',
    'name': 'Console Handler',
    'module_path': 'logging',
    'class_name': 'StreamHandler',
    'level': 'DEBUG',
    'formatter': 'simple',
    'stream': 'ext://sys.stdout',
}

# ** constant: handler_equality_fields
HANDLER_EQUALITY_FIELDS = [
    'id', 'name', 'module_path', 'class_name',
    'level', 'formatter', 'stream',
]

# ** constant: logger_aggregate_sample_data
LOGGER_AGGREGATE_SAMPLE_DATA = {
    'id': 'app',
    'name': 'App Logger',
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
    'is_root': False,
}

# ** constant: logger_equality_fields
LOGGER_EQUALITY_FIELDS = [
    'id', 'name', 'level', 'handlers', 'propagate', 'is_root',
]


# *** classes

# ** class: TestFormatterAggregate
class TestFormatterAggregate(AggregateTestBase):
    '''
    Tests for FormatterAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = FormatterAggregate

    sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    equality_fields = FORMATTER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name',   'Updated Formatter', None),
        ('format', '%(message)s',       None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FormatterAggregate:
        '''
        Override to use FormatterAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return FormatterAggregate.new(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test format_config() returns correct format and datefmt.
        '''

        # Get the formatter configuration.
        config = aggregate.format_config()

        # Assert the configuration values.
        assert config['format'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert config['datefmt'] == '%Y-%m-%d %H:%M:%S'


# ** class: TestFormatterYamlObject
class TestFormatterYamlObject(TransferObjectTestBase):
    '''
    Tests for FormatterYamlObject mapping and round-trip.
    '''

    transfer_cls = FormatterYamlObject
    aggregate_cls = FormatterAggregate

    sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    equality_fields = FORMATTER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FormatterAggregate:
        '''
        Override to use FormatterAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return FormatterAggregate.new(**(data or self.aggregate_sample_data))


# ** class: TestHandlerAggregate
class TestHandlerAggregate(AggregateTestBase):
    '''
    Tests for HandlerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = HandlerAggregate

    sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    equality_fields = HANDLER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name',  'Updated Handler', None),
        ('level', 'ERROR',           None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> HandlerAggregate:
        '''
        Override to use HandlerAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return HandlerAggregate.new(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test format_config() includes stream when set.
        '''

        # Get the handler configuration.
        config = aggregate.format_config()

        # Assert the configuration values.
        assert config['class'] == 'logging.StreamHandler'
        assert config['level'] == 'DEBUG'
        assert config['formatter'] == 'simple'
        assert config['stream'] == 'ext://sys.stdout'

    # ** test: format_config_no_optional
    def test_format_config_no_optional(self):
        '''
        Test format_config() omits stream and filename when not set.
        '''

        # Create a handler without optional stream/filename.
        handler = HandlerAggregate.new(
            id='file_handler',
            name='File Handler',
            module_path='logging',
            class_name='FileHandler',
            level='INFO',
            formatter='simple',
        )

        # Get the handler configuration.
        config = handler.format_config()

        # Assert optional fields are omitted.
        assert 'stream' not in config
        assert 'filename' not in config
        assert config['class'] == 'logging.FileHandler'
        assert config['level'] == 'INFO'


# ** class: TestHandlerYamlObject
class TestHandlerYamlObject(TransferObjectTestBase):
    '''
    Tests for HandlerYamlObject mapping and round-trip.
    '''

    transfer_cls = HandlerYamlObject
    aggregate_cls = HandlerAggregate

    sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    equality_fields = HANDLER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> HandlerAggregate:
        '''
        Override to use HandlerAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return HandlerAggregate.new(**(data or self.aggregate_sample_data))


# ** class: TestLoggerAggregate
class TestLoggerAggregate(AggregateTestBase):
    '''
    Tests for LoggerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = LoggerAggregate

    sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    equality_fields = LOGGER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name',  'Updated Logger', None),
        ('level', 'WARNING',        None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> LoggerAggregate:
        '''
        Override to use LoggerAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return LoggerAggregate.new(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test format_config() returns correct level, handlers, and propagate.
        '''

        # Get the logger configuration.
        config = aggregate.format_config()

        # Assert the configuration values.
        assert config['level'] == 'DEBUG'
        assert config['handlers'] == ['console']
        assert config['propagate'] is False

    # ** test: empty_handlers_root
    def test_empty_handlers_root(self):
        '''
        Test logger with empty handlers and is_root=True.
        '''

        # Create a root logger with empty handlers.
        logger = LoggerAggregate.new(
            id='root',
            name='Root Logger',
            level='WARNING',
            handlers=[],
            is_root=True,
        )

        # Assert root-specific attributes.
        assert logger.is_root is True
        assert logger.handlers == []
        assert logger.level == 'WARNING'


# ** class: TestLoggerYamlObject
class TestLoggerYamlObject(TransferObjectTestBase):
    '''
    Tests for LoggerYamlObject mapping and round-trip.
    '''

    transfer_cls = LoggerYamlObject
    aggregate_cls = LoggerAggregate

    sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    equality_fields = LOGGER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> LoggerAggregate:
        '''
        Override to use LoggerAggregate.new() with strict=False.
        '''

        # Create an aggregate using the custom factory.
        return LoggerAggregate.new(**(data or self.aggregate_sample_data))


# *** standalone tests

# ** test: logging_settings_from_data_success
def test_logging_settings_from_data_success():
    '''
    Test LoggingSettingsYamlObject.from_data() with full YAML data, verifying id injection.
    '''

    # Create a logging settings YAML object with full data.
    settings = LoggingSettingsYamlObject.from_data(
        formatters={
            'simple': {
                'name': 'Simple Formatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        handlers={
            'console': {
                'name': 'Console Handler',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            }
        },
        loggers={
            'app': {
                'name': 'App Logger',
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        },
    )

    # Assert formatters were created with id injection.
    assert 'simple' in settings.formatters
    formatter = settings.formatters['simple']
    assert isinstance(formatter, FormatterYamlObject)
    assert formatter.id == 'simple'
    assert formatter.name == 'Simple Formatter'

    # Assert handlers were created with id injection.
    assert 'console' in settings.handlers
    handler = settings.handlers['console']
    assert isinstance(handler, HandlerYamlObject)
    assert handler.id == 'console'
    assert handler.name == 'Console Handler'

    # Assert loggers were created with id injection.
    assert 'app' in settings.loggers
    logger = settings.loggers['app']
    assert isinstance(logger, LoggerYamlObject)
    assert logger.id == 'app'
    assert logger.name == 'App Logger'


# ** test: logging_settings_from_data_empty
def test_logging_settings_from_data_empty():
    '''
    Test LoggingSettingsYamlObject.from_data() with empty data returns empty dicts.
    '''

    # Create a logging settings YAML object with empty data.
    settings = LoggingSettingsYamlObject.from_data(
        formatters={},
        handlers={},
        loggers={},
    )

    # Assert all dictionaries are empty.
    assert settings.formatters == {}
    assert settings.handlers == {}
    assert settings.loggers == {}
