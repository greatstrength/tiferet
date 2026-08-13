"""Tiferet Interfaces Settings"""

# *** imports

# ** core
import inspect
import json
from typing import Any, Dict, NoReturn, Optional

# ** infra
from abc import ABC

# *** classes

# ** class: service_error
# >> see: @guides/interfaces.md#infrastructural-failures-serviceerror
class ServiceError(Exception):
    '''
    The exception raised for an infrastructural failure inside a service.

    Deliberately not a TiferetError subclass: an infrastructural failure --
    typically faulty configuration or a lost connection -- is not a domain
    outcome, so it is never catalogued, localized, or API-formatted. It
    reaches the top of the stack as an unhandled exception by design.
    '''

    # * attribute: error_code
    error_code: str

    # * attribute: message
    message: Optional[str]

    # * attribute: module_path
    module_path: Optional[str]

    # * attribute: class_name
    class_name: Optional[str]

    # * attribute: target_method
    target_method: Optional[str]

    # * attribute: kwargs
    kwargs: Dict[str, Any]

    # * init
    def __init__(self,
            error_code: str,
            message: Optional[str] = None,
            module_path: Optional[str] = None,
            class_name: Optional[str] = None,
            target_method: Optional[str] = None,
            **kwargs,
        ):
        '''
        Initialize the ServiceError.

        :param error_code: The infrastructural error code.
        :type error_code: str
        :param message: Optional human-readable message.
        :type message: Optional[str]
        :param module_path: The module path of the failing service.
        :type module_path: Optional[str]
        :param class_name: The class name of the failing service.
        :type class_name: Optional[str]
        :param target_method: The calling method name derived from the frame.
        :type target_method: Optional[str]
        :param kwargs: Additional error context.
        :type kwargs: dict
        '''

        # Set the error attributes.
        self.error_code = error_code
        self.message = message
        self.module_path = module_path
        self.class_name = class_name
        self.target_method = target_method
        self.kwargs = kwargs

        # Initialize with serialized error data.
        super().__init__(json.dumps({
            'error_code': error_code,
            'message': message,
            'module_path': module_path,
            'class_name': class_name,
            'target_method': target_method,
            **kwargs,
        }))

    # * method: raise_for (class)
    @classmethod
    def raise_for(cls,
            service: Any,
            error_code: str,
            message: Optional[str] = None,
            cause: Optional[Exception] = None,
            **kwargs,
        ) -> NoReturn:
        '''
        Raise a ServiceError deriving its provenance from the failing service
        and the calling frame.

        :param service: The service instance or class raising the error.
        :type service: Any
        :param error_code: The infrastructural error code.
        :type error_code: str
        :param message: Optional human-readable message.
        :type message: Optional[str]
        :param cause: Optional originating exception to chain as __cause__.
        :type cause: Optional[Exception]
        :param kwargs: Additional error context.
        :type kwargs: dict
        '''

        # Resolve the service type from either an instance or a class.
        service_type = service if isinstance(service, type) else type(service)

        # Derive the calling method name from the caller's frame.
        frame = inspect.currentframe()
        target_method = frame.f_back.f_code.co_name if frame and frame.f_back else None

        # Build the error with derived provenance.
        error = cls(
            error_code,
            message=message,
            module_path=service_type.__module__ if service is not None else None,
            class_name=service_type.__name__ if service is not None else None,
            target_method=target_method,
            **kwargs,
        )

        # Raise, chaining the cause when provided.
        raise error if cause is None else error from cause

# *** interfaces

# ** interface: service
# >> see: @guides/interfaces.md#service
class Service(ABC):
    '''
    The unified vertical contract every infrastructure concern extends --
    data access, file I/O, or middleware -- so consumers depend on a
    swappable abstraction rather than a concrete implementation.
    '''

    pass
