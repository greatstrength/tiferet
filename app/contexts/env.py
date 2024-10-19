import typing

from ..containers.app import AppContainer
from ..contexts.app import AppContext
from ..objects.container import DataAttribute
from ..services import container_service
from ..repositories.container import ContainerRepository


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

    def load_container_repository(self,
        module_path: str = 'app.repositories.container',
        class_name: str = 'YamlRepository',
        **kwargs):
        '''
        Load the container repository.

        :param module_path: The module path for the container repository.
        :type module_path: str
        :param class_name: The class name for the container repository.
        :type class_name: str
        :return: The container repository.
        :rtype: ContainerRepository
        '''

        # Load container repository.
        return container_service.import_dependency(module_path, class_name)(**kwargs)
    
    def load_app_info(self, **kwargs) -> typing.List[DataAttribute]:
        '''
        Load the app data attributes.

        :param kwargs: The app data attributes.
        :type kwargs: dict
        :return: The app data attributes.
        :rtype: list
        '''

        # Load the app data attributes.
        result = []
        for key, value in kwargs.items():
            result.append(
                DataAttribute.new(
                    id=key.replace('-', '_'),
                    type='data',
                    data={'value': value})
            )
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

        # Load the container repository.
        repo_data = dict(container_yaml_base_path='app.yml') if not container_repo else container_repo
        container_repo = self.load_container_repository(**repo_data)
        
        # Set the container and app environment variables.
        container = dict(
            flags='yaml, python') if not container else container

        
        app_data = dict(
            app_name='tiferet-cli',
            app_interface='cli') if not app else app
        app_attributes = self.load_app_info(**app_data)
        
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
