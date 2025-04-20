# *** imports

# ** infra
import pytest

# ** app
from ...models.app import *


# *** constants

# ** constant: test_app_interface
TEST_APP_INTERFACE = dict(
    id='test',
    name='Test Interface',
    description='The test interface.',
    feature_flag='test',
    data_flag='test'
)


# ** constant: test_app_repo_dependency
TEST_APP_REPO_DEPENDENCY = dict(
    attribute_id='app_repo',
    module_path='tiferet.proxies.app_mock',
    class_name='MockAppProxy',
)


# ** constant: test_error_repo_dependency
TEST_ERROR_REPO_DEPENDENCY = dict(
    attribute_id='error_repo',
    module_path='tiferet.proxies.tests.error_mock',
    class_name='MockErrorProxy',
)


# ** constant: test_feature_repo_dependency
TEST_FEATURE_REPO_DEPENDENCY = dict(
    attribute_id='feature_repo',
    module_path='tiferet.proxies.tests.feature_mock',
    class_name='MockFeatureProxy',
)


# ** constant: test_container_repo_dependency
TEST_CONTAINER_REPO_DEPENDENCY = dict(
    attribute_id='container_repo',
    module_path='tiferet.proxies.tests.container_mock',
    class_name='MockContainerProxy',
)