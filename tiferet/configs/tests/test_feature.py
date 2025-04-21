# *** constants

# ** constant: test_service_command
TEST_SERVICE_COMMAND = dict(
    attribute_id='test_service_command',
    name='Test Service Command',
    params={'param1': 'value1'},
)


# ** constant: test_service_command_with_return_to_data
TEST_SERVICE_COMMAND_WITH_RETURN_TO_DATA = dict(
    **TEST_SERVICE_COMMAND,
    return_to_data=True,
    data_key='test_key',
)


# ** constant: test_feature
TEST_FEATURE = dict(
    id='test_group.test_feature',
    name='Test Feature',
    group_id='test_group',
    feature_key='test_feature',
    description='A test feature.',
    commands=[
        TEST_SERVICE_COMMAND,
    ]
)


# ** constant: test_feature_with_return_to_data
TEST_FEATURE_WITH_RETURN_TO_DATA = dict(
    name='Test Feature with return to data',
    group_id='test_group',
    feature_key='test_feature_with_return_to_data',
    id='test_group.test_feature_with_return_to_data',
    description='A test feature with return to data.',
    commands=[
        TEST_SERVICE_COMMAND_WITH_RETURN_TO_DATA,
    ]
)


# ** constant: test_feature_with_throw_error
TEST_FEATURE_WITH_THROW_ERROR = dict(
    name='Test Feature with throw error',
    group_id='test_group',
    feature_key='test_feature_with_throw_error',
    id='test_group.test_feature_with_throw_error',
    description='A test feature with throw error.',
    commands=[
        TEST_SERVICE_COMMAND,
    ]
)


# ** constant: test_feature_with_pass_on_error
TEST_FEATURE_WITH_PASS_ON_ERROR = dict(
    name='Test Feature with pass on error',
    group_id='test_group',
    feature_key='test_feature_with_pass_on_error',
    id='test_group.test_feature_with_pass_on_error',
    description='A test feature with pass on error.',
    commands=[
        dict(
            **TEST_SERVICE_COMMAND,
            pass_on_error=True,
        )
    ]
)