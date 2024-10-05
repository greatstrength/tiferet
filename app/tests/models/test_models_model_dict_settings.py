from ...objects.object import DictSettings

def test_dict_settings_new():

    # Create the dict settings.
    dict_settings = DictSettings.new(
        coerce_key='12345',
    )

    # Assert the dict settings are correct.
    assert dict_settings.coerce_key == '12345'