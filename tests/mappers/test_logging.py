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
from tiferet.contexts.tester import (
    AggregateTesterContext,
    TransferObjectTesterContext,
)
from tiferet.domain import (
    AggregateTesterObject,
    TransferObjectTesterObject,
)

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

# *** tests

# ** tester: TestFormatterAggregate
class TestFormatterAggregate:
    '''
    Tests for FormatterAggregate construction, set_attribute, and domain-specific behavior.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind an aggregate tester context from this class's sample data.'''

        return AggregateTesterContext.from_domain(
            AggregateTesterObject(
                id=f'aggregate.{self.aggregate_cls.__name__}',
                module_path=self.aggregate_cls.__module__,
                class_name=self.aggregate_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                set_attribute_params=getattr(self, 'set_attribute_params', []),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_new
    def test_new(self, tester_context, target):
        '''Verify aggregate construction against declared expected data.'''

        tester_context.assert_new(target)

    # * method: test_set_attribute
    def test_set_attribute(self, tester_context):
        '''Verify declared set_attribute cases.'''

        tester_context.assert_set_attribute()

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

    # *** domain-specific tests

    # * test: format_config
    def test_format_config(self, target):
        '''
        Test that format_config() returns the expected formatter configuration dict.

        :param aggregate: The formatter aggregate fixture.
        :type aggregate: FormatterAggregate
        '''

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['format'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert config['datefmt'] == '%Y-%m-%d %H:%M:%S'

# ** tester: TestHandlerAggregate
class TestHandlerAggregate:
    '''
    Tests for HandlerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind an aggregate tester context from this class's sample data.'''

        return AggregateTesterContext.from_domain(
            AggregateTesterObject(
                id=f'aggregate.{self.aggregate_cls.__name__}',
                module_path=self.aggregate_cls.__module__,
                class_name=self.aggregate_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                set_attribute_params=getattr(self, 'set_attribute_params', []),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_new
    def test_new(self, tester_context, target):
        '''Verify aggregate construction against declared expected data.'''

        tester_context.assert_new(target)

    # * method: test_set_attribute
    def test_set_attribute(self, tester_context):
        '''Verify declared set_attribute cases.'''

        tester_context.assert_set_attribute()

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

    # *** domain-specific tests

    # * test: format_config
    def test_format_config(self, target):
        '''
        Test that format_config() returns the expected handler configuration dict with stream.

        :param aggregate: The handler aggregate fixture.
        :type aggregate: HandlerAggregate
        '''

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['class'] == 'logging.StreamHandler'
        assert config['level'] == 'DEBUG'
        assert config['formatter'] == 'simple'
        assert config['stream'] == 'ext://sys.stdout'

    # * test: format_config_no_optional
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

# ** tester: TestLoggerAggregate
class TestLoggerAggregate:
    '''
    Tests for LoggerAggregate construction, set_attribute, and domain-specific behavior.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind an aggregate tester context from this class's sample data.'''

        return AggregateTesterContext.from_domain(
            AggregateTesterObject(
                id=f'aggregate.{self.aggregate_cls.__name__}',
                module_path=self.aggregate_cls.__module__,
                class_name=self.aggregate_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                set_attribute_params=getattr(self, 'set_attribute_params', []),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_new
    def test_new(self, tester_context, target):
        '''Verify aggregate construction against declared expected data.'''

        tester_context.assert_new(target)

    # * method: test_set_attribute
    def test_set_attribute(self, tester_context):
        '''Verify declared set_attribute cases.'''

        tester_context.assert_set_attribute()

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

    # *** domain-specific tests

    # * test: format_config
    def test_format_config(self, target):
        '''
        Test that format_config() returns the expected logger configuration dict.

        :param aggregate: The logger aggregate fixture.
        :type aggregate: LoggerAggregate
        '''

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Get the format config.
        config = aggregate.format_config()

        # Assert the configuration contains the expected keys and values.
        assert config['level'] == 'DEBUG'
        assert config['handlers'] == ['console']
        assert config['propagate'] is False

    # * test: empty_handlers_root
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

# ** tester: TestFormatterConfigObject
class TestFormatterConfigObject:
    '''
    Tests for FormatterConfigObject mapping and round-trip.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind a transfer-object tester context from this class's sample data.'''

        return TransferObjectTesterContext.from_domain(
            TransferObjectTesterObject(
                id=f'transfer_object.{self.transfer_cls.__name__}',
                module_path=self.transfer_cls.__module__,
                class_name=self.transfer_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                aggregate_module_path=self.aggregate_cls.__module__,
                aggregate_class_name=self.aggregate_cls.__name__,
                aggregate_sample_data=self.aggregate_sample_data,
                map_kwargs=getattr(self, 'map_kwargs', {}),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_map
    def test_map(self, tester_context):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        tester_context.assert_map()

    # * method: test_from_model
    def test_from_model(self, tester_context, target):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        tester_context.assert_from_model(target)

    # * method: test_round_trip
    def test_round_trip(self, tester_context, target):
        '''Verify aggregate conversion through the transfer object and back.'''

        tester_context.assert_round_trip(target)

    transfer_cls = FormatterConfigObject
    aggregate_cls = FormatterAggregate

    sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = FORMATTER_AGGREGATE_SAMPLE_DATA

    equality_fields = FORMATTER_EQUALITY_FIELDS

# ** tester: TestHandlerConfigObject
class TestHandlerConfigObject:
    '''
    Tests for HandlerConfigObject mapping and round-trip.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind a transfer-object tester context from this class's sample data.'''

        return TransferObjectTesterContext.from_domain(
            TransferObjectTesterObject(
                id=f'transfer_object.{self.transfer_cls.__name__}',
                module_path=self.transfer_cls.__module__,
                class_name=self.transfer_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                aggregate_module_path=self.aggregate_cls.__module__,
                aggregate_class_name=self.aggregate_cls.__name__,
                aggregate_sample_data=self.aggregate_sample_data,
                map_kwargs=getattr(self, 'map_kwargs', {}),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_map
    def test_map(self, tester_context):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        tester_context.assert_map()

    # * method: test_from_model
    def test_from_model(self, tester_context, target):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        tester_context.assert_from_model(target)

    # * method: test_round_trip
    def test_round_trip(self, tester_context, target):
        '''Verify aggregate conversion through the transfer object and back.'''

        tester_context.assert_round_trip(target)

    transfer_cls = HandlerConfigObject
    aggregate_cls = HandlerAggregate

    sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = HANDLER_AGGREGATE_SAMPLE_DATA

    equality_fields = HANDLER_EQUALITY_FIELDS

# ** tester: TestLoggerConfigObject
class TestLoggerConfigObject:
    '''
    Tests for LoggerConfigObject mapping and round-trip.
    '''

    # * fixture: tester_context
    @pytest.fixture
    def tester_context(self):
        '''Bind a transfer-object tester context from this class's sample data.'''

        return TransferObjectTesterContext.from_domain(
            TransferObjectTesterObject(
                id=f'transfer_object.{self.transfer_cls.__name__}',
                module_path=self.transfer_cls.__module__,
                class_name=self.transfer_cls.__name__,
                sample_data=self.sample_data,
                equality_fields=self.equality_fields,
                field_normalizers=getattr(self, 'field_normalizers', {}),
                aggregate_module_path=self.aggregate_cls.__module__,
                aggregate_class_name=self.aggregate_cls.__name__,
                aggregate_sample_data=self.aggregate_sample_data,
                map_kwargs=getattr(self, 'map_kwargs', {}),
            ),
        )

    # * fixture: target
    @pytest.fixture
    def target(self, tester_context):
        '''Construct a fresh aggregate target for one test.'''

        return tester_context.make_target()

    # * method: test_map
    def test_map(self, tester_context):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        tester_context.assert_map()

    # * method: test_from_model
    def test_from_model(self, tester_context, target):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        tester_context.assert_from_model(target)

    # * method: test_round_trip
    def test_round_trip(self, tester_context, target):
        '''Verify aggregate conversion through the transfer object and back.'''

        tester_context.assert_round_trip(target)

    transfer_cls = LoggerConfigObject
    aggregate_cls = LoggerAggregate

    sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    aggregate_sample_data = LOGGER_AGGREGATE_SAMPLE_DATA

    equality_fields = LOGGER_EQUALITY_FIELDS

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
