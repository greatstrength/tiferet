from ...objects.object import DateSettings

def test_date_settings_new():

    # Create the date settings.
    date_settings = DateSettings.new(
        formats='YYYY-MM-DD',
    )

    # Assert the date settings are correct.
    assert date_settings.formats == 'YYYY-MM-DD'