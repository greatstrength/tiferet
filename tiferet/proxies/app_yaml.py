# *** imports

# ** app
from ..clients import yaml_client
from ..data import DataObject
from ..data.app import AppSettingsYamlData
from ..contracts.app import *


# ** proxy: app_yaml_proxy
class AppYamlProxy(AppRepository):

    # * field: config_file
    config_file: str = None

    # * method: init
    def __init__(self, app_config_file: str):
        '''
        Initialize the YAML proxy.

        :param app_config_file: The application configuration file.
        :type app_config_file: str
        '''

        # Set the configuration file.
        self.config_file = app_config_file

    # * method: list_settings
    def list_settings(self) -> list[AppSettings]:
        '''
        List all app instance settings.

        :return: A list of app settings.
        :rtype: list[AppSettings]
        '''

        # Load the app settings data from the yaml configuration file and map it to the app settings object.
        settings = yaml_client.load(
            self.config_file,
            create_data=lambda data: [
                DataObject.from_data(
                    AppSettingsYamlData,
                    id=app_id,
                    **record
                ) .map() for app_id, record in data.items()],
            start_node=lambda data: data.get('contexts'))

        # Return the list of app interface objects.
        return settings

    # * method: get_settings
    def get_settings(self, app_name: str) -> AppSettings:
        '''
        Get the app instance settings by name.

        :param app_name: The name of the app.
        :type app_name: str
        :return: The app settings.
        :rtype: AppSettings
        '''

        # Load the app settings data from the yaml configuration file.
        _data: AppSettings = yaml_client.load(
            self.config_file,
            create_data=lambda data: DataObject.from_data(
                AppSettingsYamlData,
                id=app_name, 
                **data
            ),
            start_node=lambda data: data.get('contexts').get(app_name))

        # Return the app settings object.
        # If the data is None, return None.
        try:
            return _data.map()
        except AttributeError:
            return None