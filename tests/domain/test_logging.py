"""Tests for Tiferet Domain Logging"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.logging import (
    Formatter,
    Handler,
    Logger,
    LoggingSettings,
)

# *** constants

# ** constant: formatter_sample_data
FORMATTER_SAMPLE_DATA = {
    'id': 'simple',
    'name': 'Simple Formatter',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

# ** constant: handler_sample_data
HANDLER_SAMPLE_DATA = {
    'id': 'console',
    'name': 'Console Handler',
    'module_path': 'logging',
    'class_name': 'StreamHandler',
    'level': 'INFO',
    'formatter': 'simple',
    'stream': 'ext://sys.stdout',
}

# ** constant: logger_sample_data
LOGGER_SAMPLE_DATA = {
    'id': 'app',
    'name': 'App Logger',
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': True,
}

# ** constant: root_logger_sample_data
ROOT_LOGGER_SAMPLE_DATA = {
    'id': 'root',
    'name': 'Root Logger',
    'level': 'WARNING',
    'handlers': [],
    'propagate': False,
    'is_root': True,
}

# *** testers

# ** tester: test_formatter
@use_tester(
    type='domain',
    target_cls=Formatter,
    sample_data=FORMATTER_SAMPLE_DATA,
    equality_fields=['id', 'name', 'format', 'datefmt'],
    description_cases=[
        (
            'format_config',
            (),
            {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        ),
    ],
)
class TestFormatter:
    '''Tests for Formatter construction and format_config.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Formatter construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format_config includes format and datefmt.'''

        test_ctx.assert_description()

    # * test: format_config_no_datefmt
    def test_format_config_no_datefmt(self, test_ctx) -> None:
        '''Test that format_config returns datefmt as None when not set.'''

        formatter = test_ctx.make_target(
            data={'id': 'minimal', 'name': 'Minimal Formatter', 'format': '%(message)s'},
        )
        config = formatter.format_config()

        assert config['format'] == '%(message)s'
        assert config['datefmt'] is None

# ** tester: test_handler
@use_tester(
    type='domain',
    target_cls=Handler,
    sample_data=HANDLER_SAMPLE_DATA,
    equality_fields=['id', 'name', 'module_path', 'class_name', 'level', 'formatter', 'stream'],
    description_cases=[
        (
            'format_config',
            (),
            {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
        ),
    ],
)
class TestHandler:
    '''Tests for Handler construction and format_config.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Handler construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format_config includes class, level, formatter, and stream.'''

        test_ctx.assert_description()

    # * test: format_config_no_optional
    def test_format_config_no_optional(self, test_ctx) -> None:
        '''Test that format_config omits stream and filename when not set.'''

        handler = test_ctx.make_target(
            data={
                'id': 'bare',
                'name': 'Bare Handler',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
            },
        )
        config = handler.format_config()

        assert 'stream' not in config
        assert 'filename' not in config
        assert config['class'] == 'logging.StreamHandler'
        assert config['level'] == 'DEBUG'
        assert config['formatter'] == 'simple'

# ** tester: test_logger
@use_tester(
    type='domain',
    target_cls=Logger,
    sample_data=LOGGER_SAMPLE_DATA,
    equality_fields=['id', 'name', 'level', 'handlers', 'propagate'],
    description_cases=[
        (
            'format_config',
            (),
            {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': True,
            },
        ),
    ],
)
class TestLogger:
    '''Tests for Logger construction and format_config.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Logger construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format_config includes level, handlers, and propagate.'''

        test_ctx.assert_description()

    # * test: format_config_empty_handlers
    def test_format_config_empty_handlers(self, test_ctx) -> None:
        '''Test that format_config returns handlers as [] and propagate as False.'''

        logger = test_ctx.make_target(data=ROOT_LOGGER_SAMPLE_DATA)
        config = logger.format_config()

        assert config['handlers'] == []
        assert config['propagate'] is False
        assert config['level'] == 'WARNING'

# ** tester: test_logging_settings
@use_tester(
    type='domain',
    target_cls=LoggingSettings,
    sample_data={},
    equality_fields=['version', 'disable_existing_loggers'],
    description_cases=[
        (
            'format_config',
            (),
            {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {},
                'handlers': {},
                'loggers': {},
                'root': None,
            },
        ),
    ],
)
class TestLoggingSettings:
    '''Tests for LoggingSettings construction and dictConfig assembly.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify LoggingSettings defaults.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format_config defaults to empty sections, version 1, and a None root.'''

        test_ctx.assert_description()

    # * test: format_config_assembles_sections
    def test_format_config_assembles_sections(self, test_ctx) -> None:
        '''Test that format_config assembles formatters, handlers, and the root entry.'''

        formatter = Formatter(**FORMATTER_SAMPLE_DATA)
        handler = Handler(**HANDLER_SAMPLE_DATA)
        root_logger = Logger(**ROOT_LOGGER_SAMPLE_DATA)
        config = test_ctx.make_target(
            data={
                'formatters': [FORMATTER_SAMPLE_DATA],
                'handlers': [HANDLER_SAMPLE_DATA],
                'loggers': [ROOT_LOGGER_SAMPLE_DATA],
            },
        ).format_config()

        assert config['version'] == 1
        assert config['disable_existing_loggers'] is False
        assert config['formatters']['simple'] == formatter.format_config()
        assert config['handlers']['console'] == handler.format_config()
        assert config['root'] == root_logger.format_config()
        assert 'root' not in config['loggers']

    # * test: format_config_non_root_logger
    def test_format_config_non_root_logger(self, test_ctx) -> None:
        '''Test that format_config keys non-root loggers under loggers and leaves root None.'''

        logger = Logger(**LOGGER_SAMPLE_DATA)
        config = test_ctx.make_target(
            data={'loggers': [LOGGER_SAMPLE_DATA]},
        ).format_config()

        assert config['loggers']['app'] == logger.format_config()
        assert config['root'] is None
