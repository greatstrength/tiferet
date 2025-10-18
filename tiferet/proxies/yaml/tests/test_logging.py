"""Tiferet Logging YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ....commands import TiferetError
from ....models import (
    Formatter,
    Handler,
    Logger
)
from ....data import LoggingSettingsData
from ..settings import YamlConfigurationProxy
from ..logging import LoggingYamlProxy

# *** fixtures

# ** fixture: yaml_data
@pytest.fixture
def yaml_data() -> dict:
    '''
    Fixture to provide sample YAML data for logging configurations.

    :return: Sample YAML data as a dictionary.
    :rtype: dict
    '''

    # Return sample YAML data for logging configurations.
    return {
        'logging': {
            'formatters': {
                'simple': {
                    'name': 'Simple Formatter',
                    'description': 'A simple logging formatter.',
                    'format': '%(asctime)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'name': 'Console Handler',
                    'description': 'A console logging handler.',
                    'module_path': 'logging',
                    'class_name': 'StreamHandler',
                    'level': 'INFO',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'app': {
                    'name': 'app',
                    'description': 'Application logger.',
                    'level': 'DEBUG',
                    'handlers': ['console'],
                    'propagate': True,
                    'is_root': False
                }
            }
        }
    }

# ** fixture: logging_yaml_proxy
@pytest.fixture
def logging_yaml_proxy(yaml_data: dict) -> LoggingYamlProxy:
    '''
    Fixture to create a LoggingYamlProxy instance with mocked YAML loading.
    
    :param yaml_data: Sample YAML data as a dictionary.
    :type yaml_data: dict
    :return: LoggingYamlProxy instance.
    :rtype: LoggingYamlProxy
    '''

    # Create a LoggingYamlProxy instance with a mock YAML file.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to return the sample YAML data.
    proxy.load_yaml = mock.Mock(return_value=LoggingSettingsData.from_yaml_data(
        **yaml_data.get('logging', {})
    ))

    # Return the proxy instance for use in tests.
    return proxy

# *** tests

# ** test: logging_yaml_proxy_load_yaml_success
def test_logging_yaml_proxy_load_yaml_success(yaml_data: dict):
    '''
    Test successful loading of YAML data by LoggingYamlProxy.
    
    :param yaml_data: Sample YAML data as a dictionary.
    :type yaml_data: dict
    '''
    
    # Create a LoggingYamlProxy instance with a mock YAML file.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to return the sample YAML data.
    with mock.patch.object(YamlConfigurationProxy, 'load_yaml', return_value=yaml_data) as mock_load:
        result = proxy.load_yaml(start_node=lambda data: data.get('logging', {}))

    # Assert that the result matches the expected YAML data and the mock was called once.
    assert result == yaml_data
    mock_load.assert_called_once()

# ** test: logging_yaml_proxy_load_yaml_error
def test_logging_yaml_proxy_load_yaml_error():
    '''
    Test error handling in LoggingYamlProxy load_yaml for invalid YAML.
    '''

    # Create a LoggingYamlProxy instance with a mock YAML file.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to raise an exception for invalid YAML.
    with mock.patch.object(YamlConfigurationProxy, 'load_yaml', side_effect=Exception('Invalid YAML')):
        with pytest.raises(TiferetError) as exc_info:
            proxy.load_yaml(start_node=lambda data: data.get('logging', {}))

    # Assert that the exception is raised with the correct error code and message.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_LOADING_FAILED'
    assert 'Unable to load logging configuration file' in str(exc_info.value)

# ** test: logging_yaml_proxy_list_all_success
def test_logging_yaml_proxy_list_all_success(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test successful listing of all logging configurations by LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Call the list_all method to get formatters, handlers, and loggers.
    formatters, handlers, loggers = logging_yaml_proxy.list_all()

    # Assert that the formatters, handlers, and loggers are correctly loaded.
    assert len(formatters) == 1
    assert isinstance(formatters[0], Formatter)
    assert formatters[0].id == 'simple'
    assert formatters[0].format == '%(asctime)s - %(levelname)s - %(message)s'
    assert len(handlers) == 1
    assert isinstance(handlers[0], Handler)
    assert handlers[0].id == 'console'
    assert handlers[0].level == 'INFO'
    assert len(loggers) == 1
    assert isinstance(loggers[0], Logger)
    assert loggers[0].id == 'app'
    assert loggers[0].handlers == ['console']

# ** test: logging_yaml_proxy_list_all_empty
def test_logging_yaml_proxy_list_all_empty():
    '''
    Test LoggingYamlProxy list_all with empty YAML data.
    '''

    # Create a LoggingYamlProxy instance with an empty YAML configuration.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to return empty logging settings.
    proxy.load_yaml = mock.Mock(return_value=LoggingSettingsData.from_yaml_data(
        formatters={},
        handlers={},
        loggers={}
    ))

    # Call the list_all method to get formatters, handlers, and loggers.
    formatters, handlers, loggers = proxy.list_all()

    # Assert that the lists are empty.
    assert formatters == []
    assert handlers == []
    assert loggers == []
