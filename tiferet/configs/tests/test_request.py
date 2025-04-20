# *** constants

# ** constant: test_request_context
TEST_REQUEST_CONTEXT = dict(
    feature_id='test_group.test_feature',
    headers={'Content-Type': 'application/json'},
    data={'param2': 'value2'}
)


# ** constant: test_request_feature_not_found
TEST_REQUEST_FEATURE_NOT_FOUND = dict(
    feature_id='test_group.non_existent_feature',
    headers={'Content-Type': 'application/json'},
    data={}
)


# ** constant: test_request_with_return_to_data
TEST_REQUEST_WITH_RETURN_TO_DATA = dict(
    feature_id='test_group.test_feature_with_return_to_data',
    headers={'Content-Type': 'application/json'},
    data={'param2': 'value2'}
)


# ** constant: test_request_with_throw_error
TEST_REQUEST_WITH_THROW_ERROR = dict(
    feature_id='test_group.test_feature_with_throw_error',
    headers={'Content-Type': 'application/json'},
    data={'param2': 'value2', 'throw_error': 'True'}
)


# ** constant: test_request_with_pass_on_error
TEST_REQUEST_WITH_PASS_ON_ERROR = dict(
    feature_id='test_group.test_feature_with_pass_on_error',
    headers={'Content-Type': 'application/json'},
    data={'param2': 'value2', 'throw_error': 'True'}
)


# ** constant: test_request_throw_and_pass_on_error
TEST_REQUEST_THROW_AND_PASS_ON_ERROR = dict(
    feature_id='test_group.test_feature_with_throw_and_pass_on_error',
    headers={'Content-Type': 'application/json'},
    data={'param2': 'value2', 'throw_error': 'True'}
)