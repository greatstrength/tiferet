# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..logging import *
from ...models.logging import *
from ...contracts.logging import LoggingRepository

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

# ** fixture: logger_non_root
@pytest.fixture
def logger_non_root(handler):
    '''
    Fixture to create a non-root Logger instance.
    '''
    return ModelObject.new(
        Logger,
        id='app',
        name='app',
        description='Application logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=True,
        is_root=False
    )

# ** fixture: logging_repo
@pytest.fixture
def logging_repo(formatter, handler, logger_root, logger_non_root):
    '''
    Fixture to create a mocked LoggingRepository instance.
    '''
    repo = mock.Mock(spec=LoggingRepository)
    repo.list_all.return_value = (
        [formatter],
        [handler],
        [logger_root, logger_non_root]
    )
    return repo

# ** fixture: logging_handler
@pytest.fixture
def logging_handler(logging_repo):
    '''
    Fixture to create a LoggingHandler instance with mocked repository.
    '''
    return LoggingHandler(logging_repo=logging_repo)

# *** tests

# ** test: logging_handler_list_all_success
def test_logging_handler_list_all_success(logging_handler, formatter, handler, logger_root, logger_non_root):
    '''
    Test successful listing of all logging configurations by LoggingHandler.
    '''
    # Call list_all to retrieve configurations.
    formatters, handlers, loggers = logging_handler.list_all()

    # Assert that the configurations are correctly retrieved.
    assert len(formatters) == 1
    assert formatters[0] == formatter
    assert len(handlers) == 1
    assert handlers[0] == handler
    assert len(loggers) == 2
    assert logger_root in loggers
    assert logger_non_root in loggers

# ** test: logging_handler_list_all_empty
def test_logging_handler_list_all_empty(logging_handler):
    '''
    Test LoggingHandler list_all with empty repository data.
    '''
    # Mock empty repository response.
    logging_handler.logging_repo.list_all.return_value = ([], [], [])

    # Call list_all to retrieve configurations.
    formatters, handlers, loggers = logging_handler.list_all()

    # Assert that the lists are empty.
    assert formatters == []
    assert handlers == []
    assert loggers == []

# ** test: logging_handler_format_config_success
def test_logging_handler_format_config_success(logging_handler, formatter, handler, logger_root, logger_non_root):
    '''
    Test successful formatting of logging configurations by LoggingHandler.
    '''
    # Call format_config with configurations.
    config = logging_handler.format_config(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root, logger_non_root],
        version=1,
        disable_existing_loggers=False
    )

    # Assert that the configuration is correctly formatted.
    assert config == {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'app': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': True
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        }
    }

# ** test: logging_handler_format_config_no_root
def test_logging_handler_format_config_no_root(logging_handler, formatter, handler, logger_non_root):
    '''
    Test LoggingHandler format_config with no root logger.
    '''
    # Call format_config without a root logger, expecting an error.
    with pytest.raises(TiferetError) as exc_info:
        logging_handler.format_config(
            formatters=[formatter],
            handlers=[handler],
            loggers=[logger_non_root]
        )

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'
    assert 'No root logger' in str(exc_info.value)

# ** test: logging_handler_create_logger_success
def test_logging_handler_create_logger_success(logging_handler, formatter, handler, logger_root):
    '''
    Test successful creation of a logger by LoggingHandler.
    '''
    # Mock logging.config.dictConfig and logging.getLogger.
    config = {
        'version': 1,
        'formatters': {'simple': formatter.format_config()},
        'handlers': {'console': handler.format_config()},
        'root': logger_root.format_config()
    }
    mock_logger = mock.Mock(spec=logging.Logger)
    with mock.patch('logging.config.dictConfig') as mock_dict_config:
        with mock.patch('logging.getLogger', return_value=mock_logger) as mock_get_logger:
            logger = logging_handler.create_logger('root', config)

    # Assert that the logger is created and methods are called.
    assert logger == mock_logger
    mock_dict_config.assert_called_once_with(config)
    mock_get_logger.assert_called_once_with('root')

# ** test: logging_handler_create_logger_config_error
def test_logging_handler_create_logger_config_error(logging_handler, formatter, handler, logger_root):
    '''
    Test LoggingHandler create_logger with invalid configuration.
    '''
    # Mock dictConfig to raise an exception.
    config = {
        'version': 1,
        'formatters': {'simple': formatter.format_config()},
        'handlers': {'console': handler.format_config()},
        'root': logger_root.format_config()
    }
    with mock.patch('logging.config.dictConfig', side_effect=ValueError('Invalid config')):
        with pytest.raises(TiferetError) as exc_info:
            logging_handler.create_logger('root', config)

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'
    assert 'Failed to configure logging' in str(exc_info.value)

# ** test: logging_handler_create_logger_id_error
def test_logging_handler_create_logger_id_error(logging_handler, formatter, handler, logger_root):
    '''
    Test LoggingHandler create_logger with invalid logger ID.
    '''
    # Mock dictConfig and getLogger to raise an exception.
    config = {
        'version': 1,
        'formatters': {'simple': formatter.format_config()},
        'handlers': {'console': handler.format_config()},
        'root': logger_root.format_config()
    }
    with mock.patch('logging.config.dictConfig'):
        with mock.patch('logging.getLogger', side_effect=Exception('Logger not found')):
            with pytest.raises(TiferetError) as exc_info:
                logging_handler.create_logger('invalid', config)

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGER_CREATION_FAILED'
    assert 'Failed to create logger with ID invalid' in str(exc_info.value)
