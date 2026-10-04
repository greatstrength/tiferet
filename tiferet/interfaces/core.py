"""Tiferet Interfaces Settings"""

# *** imports

# ** core
from abc import ABC
from typing import Any, Dict, NoReturn, Optional
import inspect
import json

# *** classes

# ** class: service_error
# >> see: @guides/interfaces.md#infrastructural-failures-serviceerror
class ServiceError(Exception):
    '''
    The exception raised for an infrastructural failure inside a service.

    A ServiceError is deliberately **not** a ``TiferetError`` subclass: an
    infrastructural failure — typically faulty configuration or a lost
    connection — is not a domain outcome, so it is not catalogued, not
    localized, and not formatted into an API response. If it reaches the top of
    the stack it is an unhandled exception, which is the intended behaviour.

    The failure is part of the service *contract*, which is why it lives beside
    ``Service`` rather than in the assets layer: every layer that holds a
    service already imports ``interfaces``.

    Because the error is read as a defect report rather than a response, it
    names the service instance that failed: ``module_path`` and ``class_name``
    are the same fields dependency injection used to construct the instance, so
    a service error traces back to the ``services:`` entry in the configuration
    that produced it.
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
            message: str = None,
            module_path: str = None,
            class_name: str = None,
            target_method: str = None,
            **kwargs,
        ):
        '''
        Initialize the ServiceError with an error code, message, and the
        provenance of the service that failed.

        :param error_code: The service error code.
        :type error_code: str
        :param message: The error message carried by the error itself.
        :type message: str
        :param module_path: The module path of the failing service.
        :type module_path: str
        :param class_name: The class name of the failing service.
        :type class_name: str
        :param target_method: The service method the failure occurred in.
        :type target_method: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Set the error code and message.
        self.error_code = error_code
        self.message = message

        # Set the provenance of the failing service.
        self.module_path = module_path
        self.class_name = class_name
        self.target_method = target_method

        # Set the additional error arguments.
        self.kwargs = kwargs

        # Initialize the base exception with the serialized error data.
        super().__init__(
            json.dumps({
                'error_code': error_code,
                'message': message,
                'module_path': module_path,
                'class_name': class_name,
                'target_method': target_method,
                **kwargs,
            })
        )

    # * method: raise_for (class)
    @classmethod
    def raise_for(cls,
            service: Any,
            error_code: str,
            message: str = None,
            cause: BaseException = None,
            **kwargs,
        ) -> NoReturn:
        '''
        Raise a service error for a failing service, deriving the service's
        provenance from the instance and the invocation from the calling frame.

        The classmethod form dispatches ``raise cls(...)`` to whichever subclass
        it is called on. Provenance is derived rather than hand-passed, which is
        why the failing service is the first parameter: the invocation context
        is only available at the raise site inside the service itself. A class
        may be passed in place of an instance for a static raise site.

        :param service: The failing service instance, or its class for a static
            raise site.
        :type service: Any
        :param error_code: The service error code to raise.
        :type error_code: str
        :param message: The error message to carry.
        :type message: str
        :param cause: The underlying exception that caused the failure, chained
            onto the raised error when supplied.
        :type cause: BaseException
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Resolve the service type, accepting a class for a static raise site.
        service_type = service if isinstance(service, type) else type(service)

        # Derive the invoking method from the calling frame; the inspection cost
        # sits on the failure path only.
        frame = inspect.currentframe()
        target_method = frame.f_back.f_code.co_name if frame and frame.f_back else None

        # Build the service error with the derived provenance.
        error = cls(
            error_code,
            message=message,
            module_path=service_type.__module__ if service is not None else None,
            class_name=service_type.__name__ if service is not None else None,
            target_method=target_method,
            **kwargs,
        )

        # Raise the error, chaining the underlying failure when one caused it.
        if cause is None:
            raise error
        raise error from cause

# *** interfaces

# ** interface: service
# >> see: @guides/interfaces.md#service
class Service(ABC):
    '''
    The unified vertical contract every infrastructure concern extends -
    data access, file I/O, or middleware - so consumers depend on a
    swappable abstraction rather than a concrete implementation.
    '''

    pass
