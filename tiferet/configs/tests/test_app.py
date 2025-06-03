# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...models.app import *


# *** constants

# ** constant: test_app_settings
TEST_APP_SETTINGS = dict(
    id='test',
    name='Test App',
    description='The test app.',
    feature_flag='test',
    data_flag='test',
    dependencies=[
        DEFAULT_APP_CONTEXT_DEPENDENCY,
        DEFAULT_ERROR_SERVICE_DEPENDENCY,
        DEFAULT_FEATURE_SERVICE_DEPENDENCY,
        DEFAULT_CONTAINER_SERVICE_DEPENDENCY,
        dict(
            attribute_id='error_repo',
            module_path='tiferet.proxies.tests.error_mock',
            class_name='MockErrorProxy',
        ),
        dict(
            attribute_id='feature_repo',
            module_path='tiferet.proxies.tests.feature_mock',
            class_name='MockFeatureProxy',
        ),
        dict(
            attribute_id='container_repo',
            module_path='tiferet.proxies.tests.container_mock',
            class_name='MockContainerProxy',
        ),
    ],
)


# ** constant: test_app_settings_yaml_data
TEST_APP_SETTINGS_YAML_DATA = dict(
    id='test_interface',
    name='Test Interface',
    data_flag='test_flag',
    app_context=dict(
        module_path='tests.contexts.test',
        class_name='TestContext'
    ),
    container_service=dict(
        module_path='tiferet.proxies.tests.container_mock',
        class_name='MockContainerProxy',
        parameters=dict(
            container_id='test_container',
            container_name='Test Container',
        )
    ),
    constants=dict(
        test_const='123',
    ),
)