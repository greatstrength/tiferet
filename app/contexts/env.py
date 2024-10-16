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
        
        # Set the environment variables.
        self.__dict__.update(kwargs)

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
    
    def create_app_container(env_variables: typing.Dict[str, typing.Any]) -> AppContainer:
        '''
        Create the app container.

        :param env_variables: The environment variables.
        :type env_variables: dict
        :return: The app container.
        :rtype: AppContainer
        '''

        # Create app container.
        return AppContainer(env_variables)


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