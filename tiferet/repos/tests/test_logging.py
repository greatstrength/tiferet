"""Tiferet Logging Repository Tests"""

# *** imports

# ** infra
import pytest, yaml

# ** app
from ...mappers import TransferObject, FormatterYamlObject, HandlerYamlObject, LoggerYamlObject
from ..logging import LoggingYamlRepository

# *** constants

# ** constant: test_formatter_id
TEST_FORMATTER_ID = 'test_formatter'

# ** constant: test_handler_id
TEST_HANDLER_ID = 'test_handler'

# ** constant: test_logger_id
TEST_LOGGER_ID = 'test_logger'

# ** constant: logging_data
LOGGING_DATA = {
    'logging': {
        'formatters': {
            TEST_FORMATTER_ID: {
                'name': 'Test Formatter',
                'description': 'A test formatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            TEST_HANDLER_ID: {
                'name': 'Test Handler',
                'description': 'A test handler',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'INFO',
                'formatter': TEST_FORMATTER_ID,
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            TEST_LOGGER_ID: {
                'name': 'Test Logger',
                'description': 'A test logger',
                'level': 'DEBUG',
                'handlers': [TEST_HANDLER_ID],
                'propagate': False,
                'is_root': False
            }
        }
    }
}

# *** fixtures

# ** fixture: logging_config_file
@pytest.fixture
def logging_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the logging YAML configuration file.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The logging YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample logging configuration content.
    file_path = tmp_path / 'test_logging.yaml'

    # Write the sample logging configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(LOGGING_DATA, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: logging_config_repo
@pytest.fixture
def logging_config_repo(logging_config_file: str) -> LoggingYamlRepository:
    '''
    Fixture to create an instance of the Logging Configuration Repository.

    :param logging_config_file: The logging YAML configuration file path.
    :type logging_config_file: str
    :return: An instance of LoggingYamlRepository.
    :rtype: LoggingYamlRepository
    '''

    # Create and return the LoggingYamlRepository instance.
    return LoggingYamlRepository(logging_config_file)

# *** tests

# ** test_int: logging_config_repo_list_all
def test_int_logging_config_repo_list_all(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the list_all method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # List all formatters, handlers, and loggers.
    formatters, handlers, loggers = logging_config_repo.list_all()

    # Check formatters.
    assert formatters
    assert len(formatters) == 1
    assert formatters[0].id == TEST_FORMATTER_ID
    assert formatters[0].name == 'Test Formatter'
    assert formatters[0].format == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Check handlers.
    assert handlers
    assert len(handlers) == 1
    assert handlers[0].id == TEST_HANDLER_ID
    assert handlers[0].name == 'Test Handler'
    assert handlers[0].level == 'INFO'
    assert handlers[0].formatter == TEST_FORMATTER_ID

    # Check loggers.
    assert loggers
    assert len(loggers) == 1
    assert loggers[0].id == TEST_LOGGER_ID
    assert loggers[0].name == 'Test Logger'
    assert loggers[0].level == 'DEBUG'
    assert TEST_HANDLER_ID in loggers[0].handlers

# ** test_int: logging_config_repo_save_formatter
def test_int_logging_config_repo_save_formatter(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the save_formatter method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Create constant for new test formatter.
    NEW_FORMATTER_ID = 'new_test_formatter'

    # Create new formatter.
    formatter = TransferObject.from_data(
        FormatterYamlObject,
        id=NEW_FORMATTER_ID,
        name='New Test Formatter',
        description='A new test formatter',
        format='%(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    ).map()

    # Save the formatter.
    logging_config_repo.save_formatter(formatter)

    # Reload the formatters to verify the changes.
    formatters, _, _ = logging_config_repo.list_all()

    # Check that the new formatter exists.
    formatter_ids = [f.id for f in formatters]
    assert NEW_FORMATTER_ID in formatter_ids

    # Get the new formatter and verify its attributes.
    new_formatter = next(f for f in formatters if f.id == NEW_FORMATTER_ID)
    assert new_formatter.name == 'New Test Formatter'
    assert new_formatter.format == '%(levelname)s - %(message)s'

# ** test_int: logging_config_repo_save_handler
def test_int_logging_config_repo_save_handler(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the save_handler method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Create constant for new test handler.
    NEW_HANDLER_ID = 'new_test_handler'

    # Create new handler.
    handler = TransferObject.from_data(
        HandlerYamlObject,
        id=NEW_HANDLER_ID,
        name='New Test Handler',
        description='A new test handler',
        module_path='logging',
        class_name='FileHandler',
        level='ERROR',
        formatter=TEST_FORMATTER_ID,
        filename='test.log'
    ).map()

    # Save the handler.
    logging_config_repo.save_handler(handler)

    # Reload the handlers to verify the changes.
    _, handlers, _ = logging_config_repo.list_all()

    # Check that the new handler exists.
    handler_ids = [h.id for h in handlers]
    assert NEW_HANDLER_ID in handler_ids

    # Get the new handler and verify its attributes.
    new_handler = next(h for h in handlers if h.id == NEW_HANDLER_ID)
    assert new_handler.name == 'New Test Handler'
    assert new_handler.level == 'ERROR'
    assert new_handler.class_name == 'FileHandler'

# ** test_int: logging_config_repo_save_logger
def test_int_logging_config_repo_save_logger(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the save_logger method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Create constant for new test logger.
    NEW_LOGGER_ID = 'new_test_logger'

    # Create new logger.
    logger = TransferObject.from_data(
        LoggerYamlObject,
        id=NEW_LOGGER_ID,
        name='New Test Logger',
        description='A new test logger',
        level='WARNING',
        handlers=[TEST_HANDLER_ID],
        propagate=True,
        is_root=False
    ).map()

    # Save the logger.
    logging_config_repo.save_logger(logger)

    # Reload the loggers to verify the changes.
    _, _, loggers = logging_config_repo.list_all()

    # Check that the new logger exists.
    logger_ids = [l.id for l in loggers]
    assert NEW_LOGGER_ID in logger_ids

    # Get the new logger and verify its attributes.
    new_logger = next(l for l in loggers if l.id == NEW_LOGGER_ID)
    assert new_logger.name == 'New Test Logger'
    assert new_logger.level == 'WARNING'
    assert new_logger.propagate == True

# ** test_int: logging_config_repo_delete_formatter
def test_int_logging_config_repo_delete_formatter(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the delete_formatter method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Delete an existing formatter.
    logging_config_repo.delete_formatter(TEST_FORMATTER_ID)

    # Attempt to list all formatters.
    formatters, _, _ = logging_config_repo.list_all()

    # Check that the formatter is deleted.
    formatter_ids = [f.id for f in formatters]
    assert TEST_FORMATTER_ID not in formatter_ids

# ** test_int: logging_config_repo_delete_handler
def test_int_logging_config_repo_delete_handler(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the delete_handler method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Delete an existing handler.
    logging_config_repo.delete_handler(TEST_HANDLER_ID)

    # Attempt to list all handlers.
    _, handlers, _ = logging_config_repo.list_all()

    # Check that the handler is deleted.
    handler_ids = [h.id for h in handlers]
    assert TEST_HANDLER_ID not in handler_ids

# ** test_int: logging_config_repo_delete_logger
def test_int_logging_config_repo_delete_logger(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test the delete_logger method of the LoggingYamlRepository.

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Delete an existing logger.
    logging_config_repo.delete_logger(TEST_LOGGER_ID)

    # Attempt to list all loggers.
    _, _, loggers = logging_config_repo.list_all()

    # Check that the logger is deleted.
    logger_ids = [l.id for l in loggers]
    assert TEST_LOGGER_ID not in logger_ids

# ** test_int: logging_config_repo_delete_idempotent
def test_int_logging_config_repo_delete_idempotent(
        logging_config_repo: LoggingYamlRepository,
    ):
    '''
    Test that delete methods are idempotent (no error on non-existent ID).

    :param logging_config_repo: The logging configuration repository.
    :type logging_config_repo: LoggingYamlRepository
    '''

    # Delete a non-existent formatter (should not raise error).
    logging_config_repo.delete_formatter('NON_EXISTENT_FORMATTER')

    # Delete a non-existent handler (should not raise error).
    logging_config_repo.delete_handler('NON_EXISTENT_HANDLER')

    # Delete a non-existent logger (should not raise error).
    logging_config_repo.delete_logger('NON_EXISTENT_LOGGER')

    # If we reach here, the test passes (no exceptions raised).
    assert True

# ** test_int: logging_config_repo_empty_sections
def test_int_logging_config_repo_empty_sections(tmp_path):
    '''
    Test that the repository handles empty/missing sections gracefully.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a YAML file with empty logging sections.
    file_path = tmp_path / 'empty_logging.yaml'
    empty_data = {
        'logging': {
            'formatters': {},
            'handlers': {},
            'loggers': {}
        }
    }

    # Write the empty data to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(empty_data, f)

    # Create repository instance.
    repo = LoggingYamlRepository(str(file_path))

    # List all (should return empty lists).
    formatters, handlers, loggers = repo.list_all()

    # Check that all lists are empty.
    assert len(formatters) == 0
    assert len(handlers) == 0
    assert len(loggers) == 0
