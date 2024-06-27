from typing import Dict

from .constants import APP_CONFIGURATION_FILE
from .config import load_app_config_reader, AppConfigurationReader, AppConfiguration
from .error import *
from .containers import *
from .routing import *


class AppContext():

    name: str = None
    interface: str = None
    container_config: ContainerConfiguration = None
    container: Container = None
    errors: ErrorManager = ErrorManager()
    feature_groups: dict = None

    def __init__(self, name: str, interface: str, app_config: AppConfiguration, container_config: ContainerConfiguration, container: type = Container):
        # Set app name.
        self.name = name

        # Set interface.
        self.interface = interface

        # Load app errors.
        try:
            for error_name, error in app_config.errors.items():
                self.errors.add(
                    Error({'error_name': error_name, **error.to_primitive()}))
        except AttributeError:
            pass

        self.feature_groups = app_config.features.groups

        # Load container config and container.
        self.container_config = container_config
        self.container = container(container_config)

    def run(self, **kwargs):
        pass


class AppBuilder():

    class Session():
        def __init__(self, name: str, app_config: AppConfiguration, container_config: ContainerConfiguration):
            self.name = name
            self.app_config = app_config
            self.container_config = container_config

    _current_session = None

    @property
    def app_config(self) -> AppConfiguration:
        return self._current_session.app_config

    def create_new_app(self, name: str, config_file: str = APP_CONFIGURATION_FILE, **kwargs):
        kwargs
        if self._current_session:
            self._current_session = None
        app_config_reader: AppConfigurationReader = load_app_config_reader(
            config_file)
        app_config = app_config_reader.load_config(strict=False)
        self._current_session = self.Session(
            name=name,
            app_config=app_config,
            container_config=None
        )
        return self

    def set_app_config(self, app_config: AppConfiguration):
        self._current_session.app_config = app_config
        return self

    def set_container_config(self, container_config: ContainerConfiguration):
        self._current_session.container_config = container_config
        return self

    def build(self):
        pass
