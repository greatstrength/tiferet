# *** imports


# ** infra
import pytest
from unittest import mock


# ** app
from ..logging import *
from ...configs import TiferetError
from ...assets.logging import *
from ...entities.logging import *
from ...handlers.logging import LoggingService


# *** fixtures


# ** fixture: formatter
@pytest.fixture
def formatter():
    '''
    Fixture to create a Formatter instance.
    '''
    return ModelObject.new(
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
    return ModelObject.new(
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
    return ModelObject.new(
        Logger,
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=False,
        is_root=True
    )


# ** fixture: logging_service
@pytest.fixture
def logging_service(formatter, handler, logger_root):
    '''
    Fixture to create a mocked LoggingService instance.
    '''
    service = mock.Mock(spec=LoggingService)
    service.list_all.return_value = ([formatter], [handler], [logger_root])
    service.format_config.return_value = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'simple': formatter.format_config()},
        'handlers': {'root': handler.format_config()},
        'root': logger_root.format_config()
    }
    service.create_logger.return_value = mock.Mock(spec=logging.Logger)
    return service


# ** fixture: logging_context
@pytest.fixture
def logging_context(logging_service):
    '''
    Fixture to create a LoggingContext instance.
    '''
    return LoggingContext(logging_service=logging_service, logger_id='root')


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
            'level': 'NOTSET',
            'formatter': 'default'
        }],
        'DEFAULT_LOGGERS': [{
            'id': 'root',
            'name': '',
            'description': 'Default root logger.',
            'level': 'NOTSET',
            'handlers': ['default'],
            'propagate': False,
            'is_root': True
        }]
    }


# *** tests


# ** test: logging_context_build_logger_success
def test_logging_context_build_logger_success(logging_context, logging_service, formatter, handler, logger_root):
    '''
    Test successful logger creation by LoggingContext with provided configurations.
    '''
    # Call build_logger to create a logger.
    logger = logging_context.build_logger()


    # Assert that the logger is created and methods are called.
    assert isinstance(logger, logging.Logger)
    logging_service.list_all.assert_called_once()
    logging_service.format_config.assert_called_once_with(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root]
    )
    logging_service.create_logger.assert_called_once_with(
        logger_id='root',
        logging_config=logging_service.format_config.return_value
    )


# ** test: logging_context_build_logger_default_configs
def test_logging_context_build_logger_default_configs(logging_context, logging_service, default_configs):
    '''
    Test LoggingContext build_logger using default configurations.
    '''
    # Mock empty configurations from logging_service.
    logging_service.list_all.return_value = ([], [], [])


    # Mock default configurations.
    with mock.patch('tiferet.configs.logging.DEFAULT_FORMATTERS', default_configs['DEFAULT_FORMATTERS']):
        with mock.patch('tiferet.configs.logging.DEFAULT_HANDLERS', default_configs['DEFAULT_HANDLERS']):
            with mock.patch('tiferet.configs.logging.DEFAULT_LOGGERS', default_configs['DEFAULT_LOGGERS']):
                logger = logging_context.build_logger()


    # Assert that default configurations are used.
    assert isinstance(logger, logging.Logger)
    logging_service.list_all.assert_called_once()
    logging_service.format_config.assert_called_once()
    logging_service.create_logger.assert_called_once_with(
        logger_id='root',
        logging_config=logging_service.format_config.return_value
    )


# ** test: logging_context_build_logger_error
def test_logging_context_build_logger_error(logging_context, logging_service):
    '''
    Test LoggingContext build_logger with invalid logger ID.
    '''
    # Mock create_logger to raise an error.
    logging_service.create_logger.side_effect = TiferetError(
        'LOGGER_CREATION_FAILED',
        'Failed to create logger with ID invalid: Logger not found.',
        'invalid', 
        'Logger not found'
    )


    # Call build_logger with an invalid logger ID.
    logging_context.logger_id = 'invalid'
    with pytest.raises(TiferetError) as exc_info:
        logging_context.build_logger()


    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGER_CREATION_FAILED'
    assert 'Failed to create logger with ID invalid' in str(exc_info.value)
