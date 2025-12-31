"""Tiferet Service Handler/Provider Settings"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
from dependencies import Injector

# ** app
from ..commands import raise_error

# *** objects

# ** object: service_provider
class ServiceProvider(object):
    '''
    A base class for a service provider.
    '''

    

    # * method: get_keyed_service
    def get_keyed_service(self, key: str) -> Any:
        '''
        Get a service by the name of the attribute key

        :param service_type: The type of service to retrieve.
        :type service_type: type
        :return: The requested service.
        :rtype: Any
        '''

        # Get the service by key from the injector.
        service = getattr(self, key, None)

        # If the service is not found, raise an error.
        if not service:
            raise_error.execute(
                'SERVICE_NOT_FOUND',
                None,
                key,
            )

        # Return the requested service.
        return service