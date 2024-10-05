from ...objects.object import ListSettings

def test_list_settings_new():

    # Create the list settings.
    list_settings = ListSettings.new(
        min_size=1,
        max_size=100,
    )

    # Assert the list settings are correct.
    assert list_settings.min_size == 1
    assert list_settings.max_size == 100


def test_list_settings_new_with_int_parameters_as_strings():

    # Create the list settings.
    list_settings = ListSettings.new(
        min_size='1',
        max_size='100',
    )

    # Assert the list settings are correct.
    assert list_settings.min_size == 1
    assert list_settings.max_size == 100