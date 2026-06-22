# *** imports


# ** infra
import pytest
from unittest import mock


# ** app
from tiferet.contexts.logging import *
from tiferet.assets import TiferetError
from tiferet.assets.logging import DEFAULT_FORMATTERS, DEFAULT_HANDLERS, DEFAULT_LOGGERS
from tiferet.domain.logging import Formatter, Handler, Logger


# *** fixtures


# ** fixture: formatter
@pytest.fixture
def formatter():
    '''
    Fixture to create a Formatter instance.
    '''
    return Formatter(
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# ** fixture: handler
@pytest.fixture
def handler(formatter):
    '''
    Fixture to create a Handler instance.
    '''
    return Handler(
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter.id,
        stream='ext://sys.stdout'
    )


# ** fixture: logger_root
@pytest.fixture
def logger_root(handler):
    '''
    Fixture to create a root Logger instance.
    '''
    return Logger(
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=False,
        is_root=True
    )


# ** fixture: logging_list_all_evt
@pytest.fixture
def logging_list_all_evt(formatter, handler, logger_root):
    '''
    Fixture to create a mocked ListAllLoggingConfigs event instance.
    '''
    evt = mock.Mock()
    evt.execute.return_value = ([formatter], [handler], [logger_root])
    return evt


# ** fixture: logging_context
@pytest.fixture
def logging_context(logging_list_all_evt):
    '''
    Fixture to create a LoggingContext instance.
    '''
    return LoggingContext(logging_list_all_evt=logging_list_all_evt, logger_id='root')


# ** fixture: default_configs
@pytest.fixture
def default_configs():
    '''
    Fixture to mock default logging configurations.
    '''
    return {
        'DEFAULT_FORMATTERS': [{
            'id': 'default',
            'name': 'Default Formatter',
            'description': 'A default logging formatter.',
            'format': '%(message)s',
            'datefmt': None
        }],
        'DEFAULT_HANDLERS': [{
            'id': 'default',
            'name': 'Default Handler',
            'description': 'A default logging handler.',
            'module_path': 'logging',
            'class_name': 'NullHandler',
            'level': 'INFO',
            'formatter': 'default'
        }],
        'DEFAULT_LOGGERS': [{
            'id': 'root',
            'name': '',
            'description': 'Default root logger.',
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': False,
            'is_root': True
        }]
    }


# *** tests


# ** test: logging_context_build_logger_success
def test_logging_context_build_logger_success(logging_context, logging_list_all_evt, formatter, handler, logger_root):
    '''
    Test successful logger creation by LoggingContext with provided configurations.
    '''

    # Call build_logger to create a logger.
    logger = logging_context.build_logger()

    # Assert that the logger is created and methods are called.
    assert isinstance(logger, logging.Logger)
    logging_list_all_evt.execute.assert_called_once()
    assert logger.name == 'root'


# ** test: logging_context_build_logger_default_configs
def test_logging_context_build_logger_default_configs(logging_context, logging_list_all_evt, default_configs):
    '''
    Test LoggingContext build_logger using default configurations.
    '''

    # Mock empty configurations from logging_list_all_evt.
    logging_list_all_evt.execute.return_value = ([], [], [])

    # Mock default configurations.
    with mock.patch('tiferet.contexts.logging.DEFAULT_FORMATTERS', default_configs['DEFAULT_FORMATTERS']):
        with mock.patch('tiferet.contexts.logging.DEFAULT_HANDLERS', default_configs['DEFAULT_HANDLERS']):
            with mock.patch('tiferet.contexts.logging.DEFAULT_LOGGERS', default_configs['DEFAULT_LOGGERS']):
                logger = logging_context.build_logger()

    # Assert that default configurations are used.
    assert isinstance(logger, logging.Logger)
    logging_list_all_evt.execute.assert_called_once()
    assert logger.name == 'root'


# ** test: logging_context_create_logger_success
def test_logging_context_create_logger_success(logging_context, formatter, handler, logger_root):
    '''
    Test LoggingContext create_logger successfully creates a logger.
    '''

    # Assemble the configuration via the value object.
    config = LoggingSettings(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root],
    ).format_config()

    # Create the logger.
    logger = logging_context.create_logger(
        logger_id='root',
        logging_config=config
    )

    # Assert logger is created.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'root'


# ** test: logging_context_create_logger_invalid_config
def test_logging_context_create_logger_invalid_config(logging_context):
    '''
    Test LoggingContext create_logger with invalid configuration.
    '''

    # Create an invalid configuration.
    invalid_config = {
        'version': 1,
        'formatters': {},
        'handlers': {
            'invalid': {
                'class': 'InvalidHandlerClass',
                'level': 'INFO'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['invalid']
        }
    }

    # Call create_logger with invalid config.
    with pytest.raises(TiferetError) as exc_info:
        logging_context.create_logger(
            logger_id='root',
            logging_config=invalid_config
        )

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'


# ** test: logging_context_build_logger_error
def test_logging_context_build_logger_error(logging_context, logging_list_all_evt):
    '''
    Test LoggingContext build_logger with configurations that fail dictConfig.
    '''

    # Mock list_all to return invalid configurations that will fail.
    invalid_formatter = Formatter(
        id='invalid',
        name='Invalid Formatter',
        description='An invalid formatter.',
        format='%(invalid)s',
        datefmt=None
    )
    logging_list_all_evt.execute.return_value = ([invalid_formatter], [], [])

    # Call build_logger with invalid configurations.
    with pytest.raises(TiferetError) as exc_info:
        logging_context.build_logger()

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'
