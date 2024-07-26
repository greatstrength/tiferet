from typing import Any, Dict

from ..contexts.request import RequestContext
from ..containers.app import AppContainer

def create_request(self, request: Any, **kwargs) -> RequestContext:
    return RequestContext(request)


def load_environment_variables(env_base_key: str) -> Any:
    
    # Import os module.
    import os

    # Create result dictionary.
    result = {}

    # Iterate over environment variables.
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

    # Return result.
    return result


def create_app_container(env: Dict[str, Any]):

    # Create app container.
    return AppContainer(**env.get('container'))