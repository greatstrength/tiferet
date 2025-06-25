# *** imports

# ** core
from typing import Any, Dict

# ** infra
from dependencies import Injector
from dependencies.exceptions import DependencyError

# ** app
from ..commands import *


# *** commands

# ** command: create_injector
class CreateInjector(Command):
    '''
    A command to create a dependencies (library) injector object with the given dependencies.
    '''

    def execute(self, name: str, dependencies: Dict[str, type], **kwargs) -> Any:
        '''
        Execute the command to create an injector object.

        :param name: The name of the injector.
        :type name: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        :return: The injector object.
        :rtype: Any
        '''
    
        # Create container.
        return type(name, (Injector,), {**dependencies, **kwargs})


# ** command: get_dependency
class GetDependency(Command):
    '''
    A command to get a dependency from the injector.
    '''

    def execute(self, injector: Injector, dependency_name: str) -> Any:
        '''
        Execute the command to get a dependency from the injector.

        :param injector: The injector object.
        :type injector: Injector
        :param dependency_name: The name of the dependency to get.
        :type dependency_name: str
        :return: The dependency object.
        :rtype: Any
        '''
    
        # Return the dependency from the injector.
        try:
            return getattr(injector, dependency_name)
        
        # If the dependency does not exist or cannot be resolved, raise an error.
        except DependencyError as e:
            self.raise_error(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {dependency_name} could not be resolved: {str(e)}',
                dependency_name,
                str(e)
            )


# *** command_variables

# ** command_variable: create_injector
create_injector = CreateInjector()

# ** command_variable: get_dependency
get_dependency = GetDependency()