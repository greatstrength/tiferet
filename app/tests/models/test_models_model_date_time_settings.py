from ...objects.object import DateTimeSettings

def test_date_time_settings_new():

    # Create the date time settings.
    date_time_settings = DateTimeSettings.new(
        formats='YYYY-MM-DD HH:MM:SS',
    )

    # Assert the date time settings are correct.
    assert date_time_settings.formats == 'YYYY-MM-DD HH:MM:SS'


def test_date_time_settings_convert_tz_info_is_true():

    # Create the date time settings.
    date_time_settings = DateTimeSettings.new(
        formats='YYYY-MM-DD HH:MM:SS',
        convert_tz=True,
    )

    # Assert the date time settings are correct.
    assert date_time_settings.convert_tz is True
    assert date_time_settings.formats == 'YYYY-MM-DD HH:MM:SS'
    assert date_time_settings.drop_tzinfo is True