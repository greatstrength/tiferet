# *** imports

# ** core
from typing import Any

# ** app
from ..domain import AppInterface
from ..repos.app import AppRepository
from . import container_service


# *** functions

# ** function: load_app_context
def load_app_context(interface_id: str, app_repo: AppRepository) -> Any:
    '''
    Load the app context.

    :param container: The app container.
    :type container: AppContainer
    :return: The app context.
    :rtype: Any
    '''

    # Get the app interface.
    app_interface: AppInterface = app_repo.get_interface(interface_id)

    # Get the default dependencies for the app interface.
    app_context = app_interface.get_dependency('app_context')
    dependencies = dict(
        interface_id=app_interface.id,
        app_name=app_interface.name,
        feature_flag=app_interface.feature_flag,
        data_flag=app_interface.data_flag,
        app_context=container_service.import_dependency(
            **app_context.to_primitive()
        ),
        **app_interface.constants
    )

    # Import the dependencies.
    for dep in app_interface.dependencies:
        dependencies[dep.attribute_id] = container_service.import_dependency(dep.module_path, dep.class_name)

    # Create the injector from the dependencies, constants, and the app interface.
    injector = container_service.create_injector(
        app_interface.id,
        **dependencies
    )

    # Return the app context.
    return getattr(injector, 'app_context')