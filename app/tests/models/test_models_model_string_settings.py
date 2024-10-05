from ...objects.object import StringSettings

def test_string_settings_new():

    # Create the string settings.
    string_settings = StringSettings.new(
        regex='^.*$',
        min_length=1,
        max_length=100,
    )

    # Assert the string settings are correct.
    assert string_settings.regex == '^.*$'
    assert string_settings.min_length == 1
    assert string_settings.max_length == 100


def test_string_settings_new_with_int_parameters_as_strings():

    # Create the string settings.
    string_settings = StringSettings.new(
        regex='^.*$',
        min_length='1',
        max_length='100',
    )

    # Assert the string settings are correct.
    assert string_settings.regex == '^.*$'
    assert string_settings.min_length == 1
    assert string_settings.max_length == 100