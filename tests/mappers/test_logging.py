"""Tiferet Logging Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.mappers.core import TransferObject
from tiferet.mappers.logging import (
    FormatterAggregate,
    FormatterConfigObject,
    HandlerAggregate,
    HandlerConfigObject,
    LoggerAggregate,
    LoggerConfigObject,
    LoggingSettingsConfigObject,
)
from tiferet.assets.core import (
    create_aggregate_tester,
    create_transfer_object_tester,
)


# *** classes

# ** class: mapper_test_support
class _MapperTestSupport:
    '''Provide fixtures and nested assertions for bespoke mapper behavior tests.'''

    aggregate_cls: type
    sample_data: dict = {}
    aggregate_sample_data: dict = {}

    def make_aggregate(self, data: dict = None):
        '''Construct the declared aggregate from supplied or sample data.'''

        return self.aggregate_cls(**(
            data if data is not None
            else self.aggregate_sample_data or self.sample_data
        ))

    @pytest.fixture
    def aggregate(self):
        '''Provide a fresh aggregate for a bespoke behavior assertion.'''

        return self.make_aggregate()

    def assert_nested_list_matches(
            self,
            actual_list: list,
            expected_list: list,
            key_field: str,
            compare_fields: list,
        ) -> None:
        '''Assert two keyed lists of model objects carry matching selected fields.'''

        actual_by_key = {getattr(item, key_field): item for item in actual_list}
        expected_by_key = {getattr(item, key_field): item for item in expected_list}

        assert set(actual_by_key) == set(expected_by_key)
        for key, expected in expected_by_key.items():
            actual = actual_by_key[key]
            for field in compare_fields:
                assert getattr(actual, field) == getattr(expected, field)

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
HANDLER_EQUALITY_FIELDS = ['id', 'name', 'module_path', 'class_name', 'level', 'formatter', 'stream']

# ** constant: logger_aggregate_sample_data
LOGGER_AGGREGATE_SAMPLE_DATA = {
    'id': 'app',
    'name': 'App Logger',
    'level': 'DEBUG',
    'handlers': ['console'],
}

# ** constant: logger_equality_fields
LOGGER_EQUALITY_FIELDS = ['id', 'name', 'level', 'handlers']


# *** classes

# ** class: TestFormatterAggregate
class TestFormatterAggregate(_MapperTestSupport):
    '''
    Tests for FormatterAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = FormatterAggregate

    sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    equality_fields = FORMATTER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Formatter', None),
        ('format', '%(message)s', None),
        # invalid
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FormatterAggregate:
        '''
        Override to use FormatterAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return FormatterAggregate(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test that format_config() returns the expected formatter configuration dict.

        :param aggregate: The formatter aggregate fixture.
        :type aggregate: FormatterAggregate
        '''

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['format'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert config['datefmt'] == '%Y-%m-%d %H:%M:%S'


# ** class: TestHandlerAggregate
class TestHandlerAggregate(_MapperTestSupport):
    '''
    Tests for HandlerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = HandlerAggregate

    sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    equality_fields = HANDLER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Handler', None),
        ('level', 'ERROR', None),
        # invalid
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> HandlerAggregate:
        '''
        Override to use HandlerAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return HandlerAggregate(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test that format_config() returns the expected handler configuration dict with stream.

        :param aggregate: The handler aggregate fixture.
        :type aggregate: HandlerAggregate
        '''

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['class'] == 'logging.StreamHandler'
        assert config['level'] == 'DEBUG'
        assert config['formatter'] == 'simple'
        assert config['stream'] == 'ext://sys.stdout'

    # ** test: format_config_no_optional
    def test_format_config_no_optional(self):
        '''
        Test that format_config() omits stream and filename when not set.
        '''

        # Create a handler without optional stream/filename.
        handler = HandlerAggregate(
            id='file_handler',
            name='File Handler',
            module_path='logging',
            class_name='FileHandler',
            level='INFO',
            formatter='simple',
        )

        # Get the format config.
        config = handler.format_config()

        # Assert stream and filename are omitted.
        assert 'stream' not in config
        assert 'filename' not in config
        assert config['class'] == 'logging.FileHandler'
        assert config['level'] == 'INFO'


# ** class: TestLoggerAggregate
class TestLoggerAggregate(_MapperTestSupport):
    '''
    Tests for LoggerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    aggregate_cls = LoggerAggregate

    sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    equality_fields = LOGGER_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Logger', None),
        ('level', 'ERROR', None),
        # invalid
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> LoggerAggregate:
        '''
        Override to use LoggerAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return LoggerAggregate(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: format_config
    def test_format_config(self, aggregate):
        '''
        Test that format_config() returns the expected logger configuration dict.

        :param aggregate: The logger aggregate fixture.
        :type aggregate: LoggerAggregate
        '''

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['level'] == 'DEBUG'
        assert config['handlers'] == ['console']
        assert config['propagate'] is False

    # ** test: empty_handlers_root
    def test_empty_handlers_root(self):
        '''
        Test creating a logger with empty handlers and is_root=True.
        '''

        # Create a root logger with empty handlers.
        logger = LoggerAggregate(
            id='root',
            name='Root Logger',
            level='WARNING',
            handlers=[],
            is_root=True,
        )

        # Assert the logger attributes.
        assert logger.is_root is True
        assert logger.handlers == []
        assert logger.level == 'WARNING'


# ** class: TestFormatterConfigObject
class TestFormatterConfigObject(_MapperTestSupport):
    '''
    Tests for FormatterConfigObject mapping and round-trip.
    '''

    transfer_cls = FormatterConfigObject
    aggregate_cls = FormatterAggregate

    sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    equality_fields = FORMATTER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FormatterAggregate:
        '''
        Override to use FormatterAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return FormatterAggregate(**(data or self.aggregate_sample_data))


# ** class: TestHandlerConfigObject
class TestHandlerConfigObject(_MapperTestSupport):
    '''
    Tests for HandlerConfigObject mapping and round-trip.
    '''

    transfer_cls = HandlerConfigObject
    aggregate_cls = HandlerAggregate

    sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    equality_fields = HANDLER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> HandlerAggregate:
        '''
        Override to use HandlerAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return HandlerAggregate(**(data or self.aggregate_sample_data))


# ** class: TestLoggerConfigObject
class TestLoggerConfigObject(_MapperTestSupport):
    '''
    Tests for LoggerConfigObject mapping and round-trip.
    '''

    transfer_cls = LoggerConfigObject
    aggregate_cls = LoggerAggregate

    sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    equality_fields = LOGGER_EQUALITY_FIELDS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> LoggerAggregate:
        '''
        Override to use LoggerAggregate() which defaults to strict=False.
        '''

        # Create an aggregate using the custom factory.
        return LoggerAggregate(**(data or self.aggregate_sample_data))


# *** standalone tests

# ** test: logging_settings_from_data_success
def test_logging_settings_from_data_success():
    '''
    Test LoggingSettingsConfigObject.from_data() with full YAML data and id injection.
    '''

    # Create a logging settings YAML object with full data.
    settings = LoggingSettingsConfigObject.from_data(
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
    assert isinstance(formatter, FormatterConfigObject)
    assert formatter.id == 'simple'
    assert formatter.name == 'Simple Formatter'

    # Assert handlers were created with id injection.
    assert 'console' in settings.handlers
    handler = settings.handlers['console']
    assert isinstance(handler, HandlerConfigObject)
    assert handler.id == 'console'
    assert handler.name == 'Console Handler'

    # Assert loggers were created with id injection.
    assert 'app' in settings.loggers
    logger = settings.loggers['app']
    assert isinstance(logger, LoggerConfigObject)
    assert logger.id == 'app'
    assert logger.name == 'App Logger'


# ** test: logging_settings_from_data_empty
def test_logging_settings_from_data_empty():
    '''
    Test LoggingSettingsConfigObject.from_data() with empty dicts.
    '''

    # Create a logging settings YAML object with empty data.
    settings = LoggingSettingsConfigObject.from_data(
        formatters={},
        handlers={},
        loggers={},
    )

    # Assert all dictionaries are empty.
    assert settings.formatters == {}
    assert settings.handlers == {}
    assert settings.loggers == {}

# *** generated tests

TestFormatterAggregateGenerated = create_aggregate_tester(
    aggregate_cls=TestFormatterAggregate.aggregate_cls,
    sample_data=TestFormatterAggregate.sample_data,
    equality_fields=TestFormatterAggregate.equality_fields,
    set_attribute_params=TestFormatterAggregate.set_attribute_params,
)

TestHandlerAggregateGenerated = create_aggregate_tester(
    aggregate_cls=TestHandlerAggregate.aggregate_cls,
    sample_data=TestHandlerAggregate.sample_data,
    equality_fields=TestHandlerAggregate.equality_fields,
    set_attribute_params=TestHandlerAggregate.set_attribute_params,
)

TestLoggerAggregateGenerated = create_aggregate_tester(
    aggregate_cls=TestLoggerAggregate.aggregate_cls,
    sample_data=TestLoggerAggregate.sample_data,
    equality_fields=TestLoggerAggregate.equality_fields,
    set_attribute_params=TestLoggerAggregate.set_attribute_params,
)

TestFormatterConfigObjectGenerated = create_transfer_object_tester(
    transfer_cls=TestFormatterConfigObject.transfer_cls,
    aggregate_cls=TestFormatterConfigObject.aggregate_cls,
    sample_data=TestFormatterConfigObject.sample_data,
    aggregate_sample_data=TestFormatterConfigObject.aggregate_sample_data,
    equality_fields=TestFormatterConfigObject.equality_fields,
)

TestHandlerConfigObjectGenerated = create_transfer_object_tester(
    transfer_cls=TestHandlerConfigObject.transfer_cls,
    aggregate_cls=TestHandlerConfigObject.aggregate_cls,
    sample_data=TestHandlerConfigObject.sample_data,
    aggregate_sample_data=TestHandlerConfigObject.aggregate_sample_data,
    equality_fields=TestHandlerConfigObject.equality_fields,
)

TestLoggerConfigObjectGenerated = create_transfer_object_tester(
    transfer_cls=TestLoggerConfigObject.transfer_cls,
    aggregate_cls=TestLoggerConfigObject.aggregate_cls,
    sample_data=TestLoggerConfigObject.sample_data,
    aggregate_sample_data=TestLoggerConfigObject.aggregate_sample_data,
    equality_fields=TestLoggerConfigObject.equality_fields,
)
