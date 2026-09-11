"""Tiferet Logging Repository Tests"""

# *** imports

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.mappers import FormatterConfigObject, HandlerConfigObject, LoggerConfigObject
from tiferet.repos.logging import LoggingConfigRepository

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

# *** testers

# ** tester: test_logging_config_repository
@use_tester(
    type='repo',
    target_cls=LoggingConfigRepository,
    config_parameter='logging_config',
)
class TestLoggingConfigRepository:
    '''LoggingConfigRepository construction plus bespoke formatter/handler/logger methods.'''

    # * test: new
    def test_new(self, test_ctx, logging_config_file: str) -> None:
        '''Verify repository construction and default_role.'''

        test_ctx.assert_new(config_file=logging_config_file)

    # * test: format_dispatch
    def test_format_dispatch(self, test_ctx, tmp_path) -> None:
        '''Verify YAML and JSON payload round-trip.'''

        yaml_file = tmp_path / 'dispatch.yaml'
        json_file = tmp_path / 'dispatch.json'
        yaml_file.write_text('root: {}\n', encoding='utf-8')
        json_file.write_text('{"root": {}}\n', encoding='utf-8')
        test_ctx.assert_format_dispatch(str(yaml_file), str(json_file))

    # * test: list_all
    def test_list_all(self, test_ctx, logging_config_file: str) -> None:
        '''Test the list_all method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        formatters, handlers, loggers = repo.list_all()

        assert formatters
        assert len(formatters) == 1
        assert formatters[0].id == TEST_FORMATTER_ID
        assert formatters[0].name == 'Test Formatter'
        assert formatters[0].format == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        assert handlers
        assert len(handlers) == 1
        assert handlers[0].id == TEST_HANDLER_ID
        assert handlers[0].name == 'Test Handler'
        assert handlers[0].level == 'INFO'
        assert handlers[0].formatter == TEST_FORMATTER_ID

        assert loggers
        assert len(loggers) == 1
        assert loggers[0].id == TEST_LOGGER_ID
        assert loggers[0].name == 'Test Logger'
        assert loggers[0].level == 'DEBUG'
        assert TEST_HANDLER_ID in loggers[0].handlers

    # * test: save_formatter
    def test_save_formatter(self, test_ctx, logging_config_file: str) -> None:
        '''Test the save_formatter method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        NEW_FORMATTER_ID = 'new_test_formatter'
        formatter = FormatterConfigObject.model_validate(dict(
            id=NEW_FORMATTER_ID,
            name='New Test Formatter',
            description='A new test formatter',
            format='%(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )).map()

        repo.save_formatter(formatter)
        formatters, _, _ = repo.list_all()

        formatter_ids = [f.id for f in formatters]
        assert NEW_FORMATTER_ID in formatter_ids
        new_formatter = next(f for f in formatters if f.id == NEW_FORMATTER_ID)
        assert new_formatter.name == 'New Test Formatter'
        assert new_formatter.format == '%(levelname)s - %(message)s'

    # * test: save_handler
    def test_save_handler(self, test_ctx, logging_config_file: str) -> None:
        '''Test the save_handler method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        NEW_HANDLER_ID = 'new_test_handler'
        handler = HandlerConfigObject.model_validate(dict(
            id=NEW_HANDLER_ID,
            name='New Test Handler',
            description='A new test handler',
            module_path='logging',
            class_name='FileHandler',
            level='ERROR',
            formatter=TEST_FORMATTER_ID,
            filename='test.log'
        )).map()

        repo.save_handler(handler)
        _, handlers, _ = repo.list_all()

        handler_ids = [h.id for h in handlers]
        assert NEW_HANDLER_ID in handler_ids
        new_handler = next(h for h in handlers if h.id == NEW_HANDLER_ID)
        assert new_handler.name == 'New Test Handler'
        assert new_handler.level == 'ERROR'
        assert new_handler.class_name == 'FileHandler'

    # * test: save_logger
    def test_save_logger(self, test_ctx, logging_config_file: str) -> None:
        '''Test the save_logger method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        NEW_LOGGER_ID = 'new_test_logger'
        logger = LoggerConfigObject.model_validate(dict(
            id=NEW_LOGGER_ID,
            name='New Test Logger',
            description='A new test logger',
            level='WARNING',
            handlers=[TEST_HANDLER_ID],
            propagate=True,
            is_root=False
        )).map()

        repo.save_logger(logger)
        _, _, loggers = repo.list_all()

        logger_ids = [l.id for l in loggers]
        assert NEW_LOGGER_ID in logger_ids
        new_logger = next(l for l in loggers if l.id == NEW_LOGGER_ID)
        assert new_logger.name == 'New Test Logger'
        assert new_logger.level == 'WARNING'
        assert new_logger.propagate == True

    # * test: delete_formatter
    def test_delete_formatter(self, test_ctx, logging_config_file: str) -> None:
        '''Test the delete_formatter method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        repo.delete_formatter(TEST_FORMATTER_ID)
        formatters, _, _ = repo.list_all()

        formatter_ids = [f.id for f in formatters]
        assert TEST_FORMATTER_ID not in formatter_ids

    # * test: delete_handler
    def test_delete_handler(self, test_ctx, logging_config_file: str) -> None:
        '''Test the delete_handler method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        repo.delete_handler(TEST_HANDLER_ID)
        _, handlers, _ = repo.list_all()

        handler_ids = [h.id for h in handlers]
        assert TEST_HANDLER_ID not in handler_ids

    # * test: delete_logger
    def test_delete_logger(self, test_ctx, logging_config_file: str) -> None:
        '''Test the delete_logger method of the LoggingConfigRepository.'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        repo.delete_logger(TEST_LOGGER_ID)
        _, _, loggers = repo.list_all()

        logger_ids = [l.id for l in loggers]
        assert TEST_LOGGER_ID not in logger_ids

    # * test: delete_idempotent
    def test_delete_idempotent(self, test_ctx, logging_config_file: str) -> None:
        '''Test that delete methods are idempotent (no error on non-existent ID).'''

        repo = test_ctx.make_target(config_file=logging_config_file)
        repo.delete_formatter('NON_EXISTENT_FORMATTER')
        repo.delete_handler('NON_EXISTENT_HANDLER')
        repo.delete_logger('NON_EXISTENT_LOGGER')

        assert True

    # * test: empty_sections
    def test_empty_sections(self, test_ctx, tmp_path) -> None:
        '''Test that the repository handles empty/missing sections gracefully.'''

        file_path = tmp_path / 'empty_logging.yaml'
        empty_data = {
            'logging': {
                'formatters': {},
                'handlers': {},
                'loggers': {}
            }
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(empty_data, f)

        repo = test_ctx.make_target(config_file=str(file_path))
        formatters, handlers, loggers = repo.list_all()

        assert len(formatters) == 0
        assert len(handlers) == 0
        assert len(loggers) == 0
