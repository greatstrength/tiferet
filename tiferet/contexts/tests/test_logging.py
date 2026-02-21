# *** imports


# ** infra
import pytest
from unittest import mock


# ** app
from ..logging import *
from ...assets import TiferetError
from ...assets.logging import *
from ...domain.logging import *


# *** fixtures


# ** fixture: formatter
@pytest.fixture
def formatter():
    '''
    Fixture to create a Formatter instance.
    '''
    return DomainObject.new(
        Formatter,
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
    return DomainObject.new(
        Handler,
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
    return DomainObject.new(
        Logger,
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=False,
        is_root=True
    )


# ** fixture: list_all_cmd
@pytest.fixture
def list_all_cmd(formatter, handler, logger_root):
    '''
    Fixture to create a mocked ListAllLoggingConfigs command instance.
    '''
    cmd = mock.Mock()
    cmd.execute.return_value = ([formatter], [handler], [logger_root])
    return cmd


# ** fixture: logging_context
@pytest.fixture
def logging_context(list_all_cmd):
    '''
    Fixture to create a LoggingContext instance.
    '''
    return LoggingContext(list_all_cmd=list_all_cmd, logger_id='root')


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
def test_logging_context_build_logger_success(logging_context, list_all_cmd, formatter, handler, logger_root):
    '''
    Test successful logger creation by LoggingContext with provided configurations.
    '''
    # Call build_logger to create a logger.
    logger = logging_context.build_logger()


    # Assert that the logger is created and methods are called.
    assert isinstance(logger, logging.Logger)
    list_all_cmd.execute.assert_called_once()
    assert logger.name == 'root'


# ** test: logging_context_build_logger_default_configs
def test_logging_context_build_logger_default_configs(logging_context, list_all_cmd, default_configs):
    '''
    Test LoggingContext build_logger using default configurations.
    '''
    # Mock empty configurations from list_all_cmd.
    list_all_cmd.execute.return_value = ([], [], [])


    # Mock default configurations.
    with mock.patch('tiferet.contexts.logging.DEFAULT_FORMATTERS', default_configs['DEFAULT_FORMATTERS']):
        with mock.patch('tiferet.contexts.logging.DEFAULT_HANDLERS', default_configs['DEFAULT_HANDLERS']):
            with mock.patch('tiferet.contexts.logging.DEFAULT_LOGGERS', default_configs['DEFAULT_LOGGERS']):
                logger = logging_context.build_logger()


    # Assert that default configurations are used.
    assert isinstance(logger, logging.Logger)
    list_all_cmd.execute.assert_called_once()
    assert logger.name == 'root'


# ** test: logging_context_format_config_success
def test_logging_context_format_config_success(logging_context, formatter, handler, logger_root):
    '''
    Test LoggingContext format_config successfully formats logging configurations.
    '''
    # Call format_config to format the configurations.
    config = logging_context.format_config(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root]
    )


    # Assert the configuration structure.
    assert config['version'] == 1
    assert config['disable_existing_loggers'] is False
    assert 'formatters' in config
    assert 'handlers' in config
    assert 'root' in config
    assert formatter.id in config['formatters']
    assert handler.id in config['handlers']
    assert config['root'] == logger_root.format_config()


# ** test: logging_context_format_config_non_root_logger
def test_logging_context_format_config_non_root_logger(logging_context, formatter, handler):
    '''
    Test LoggingContext format_config with non-root logger.
    '''
    # Create a non-root logger.
    non_root_logger = DomainObject.new(
        Logger,
        id='app',
        name='app',
        description='Application logger.',
        level='INFO',
        handlers=[handler.id],
        propagate=True,
        is_root=False
    )


    # Call format_config.
    config = logging_context.format_config(
        formatters=[formatter],
        handlers=[handler],
        loggers=[non_root_logger]
    )


    # Assert non-root logger is in loggers section.
    assert 'loggers' in config
    assert non_root_logger.id in config['loggers']
    assert config['root'] is None


# ** test: logging_context_create_logger_success
def test_logging_context_create_logger_success(logging_context, formatter, handler, logger_root):
    '''
    Test LoggingContext create_logger successfully creates a logger.
    '''
    # Format the configurations.
    config = logging_context.format_config(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root]
    )


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
                'class': 'InvalidHandlerClass',  # Invalid handler class
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
def test_logging_context_build_logger_error(logging_context, list_all_cmd):
    '''
    Test LoggingContext build_logger with invalid configuration.
    '''
    # Mock list_all to return invalid configurations that will fail.
    invalid_formatter = DomainObject.new(
        Formatter,
        id='invalid',
        name='Invalid Formatter',
        description='An invalid formatter.',
        format='%(invalid)s',  # Invalid format
        datefmt=None
    )
    list_all_cmd.execute.return_value = ([invalid_formatter], [], [])


    # Call build_logger with invalid configurations.
    with pytest.raises(TiferetError) as exc_info:
        logging_context.build_logger()


    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'
