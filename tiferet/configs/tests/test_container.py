# *** constants


# ** constant: test_container_dependency
TEST_CONTAINER_DEPENDENCY = dict(
    module_path='tiferet.proxies.tests',
    class_name='TestProxy',
    flag='test',
    parameters=dict(
        config_file='tiferet/configs/tests/test.yml'
    )
)

# ** constant: test_container_attribute
TEST_CONTAINER_ATTRIBUTE = dict(
    id='test_repo',
    type='data',
    dependencies=[
        TEST_CONTAINER_DEPENDENCY
    ]
)

# ** constant: test_service_command
TEST_SERVICE_COMMAND_ATTRIBUTE = dict(
    id='test_service_command',
    type='feature',
    dependencies=[
        dict(
            module_path='tiferet.commands.tests.test_settings',
            class_name='TestServiceCommand',
            flag='test',
        )
    ]
)