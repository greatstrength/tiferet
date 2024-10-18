import typing

from ..containers.app import AppContainer
from ..contexts.app import AppContext


class EnvironmentContext(object):

    def __init__(self, env_base_key: str, **kwargs):
        '''
        Initialize the environment context.

        :param env_base_key: The base key for the environment variables.
        :type env_base_key: str
        '''

        # Load the environment variables.
        env_variables = self.load_environment_variables(env_base_key)

        # Create the app container.
        container = self.create_app_container(env_variables)

        # Load the app context.
        app_context = self.load_app_context(container)

        # Run the app context.
        app_context.run(
            container=container)

    def load_environment_variables(self, env_base_key: str) -> typing.Dict[str, typing.Any]:
        '''
        Load the environment variables.

        :param env_base_key: The base key for the environment variables.
        :type env_base_key: str
        :return: The environment variables.
        :rtype: dict
        '''

        # Load the environment variables.
        import os
        result = {}
        for key, value in os.environ.items():
            # Check if key is a valid environment variable.
            try:
                app, group, variable = key.split('__')
            except:
                continue
            # Check if key is a valid environment variable.
            if app != env_base_key:
                continue
            # Add environment variable to result.
            group = group.lower()
            if group not in result:
                result[group] = {}
            result[group][variable.lower()] = value
        return result

    def create_app_container(self, 
                             container: typing.Dict[str, str] = None, 
                             container_repo: typing.Dict[str, str] = None, 
                             app: typing.Dict[str, str] = None) -> AppContainer:
        '''
        Create the app container.

        :param container: The container environment variables.
        :type container: dict
        :param container_repo: The container repository environment variables.
        :type container_repo: dict
        :param app: The app environment variables.
        :type app: dict
        :return: The app container.
        :rtype: AppContainer
        '''

        # Set default values for the environment variables.
        container_repo = dict(
            module_path='app.repositories.container',
            class_name='YamlRepository',
            container_yaml_base_path='app.yml')
        container = dict(
            flags='yaml, python')
        app = dict(
            app_name='tiferet-cli',
            app_interface='cli')

        # Create app container.
        return AppContainer(container_repo=container_repo, container=container, app=app)

    def load_app_context(self, container: AppContainer) -> AppContext:
        '''
        Load the app context.

        :param container: The app container.
        :type container: AppContainer
        :return: The app context.
        :rtype: AppContext
        '''

        # Create the app context.
        return container.cli_interface_context
