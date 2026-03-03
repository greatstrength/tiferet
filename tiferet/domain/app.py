"""Tiferet App Domain Models"""

# *** imports

# ** app
from .settings import (
    DomainObject,
    StringType,
    ListType,
    DictType,
    ModelType,
)

# *** models

# ** model: app_service_dependency
class AppServiceDependency(DomainObject):
    '''
    An app service dependency that defines the service configuration for an app interface.
    '''

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path for the app dependency.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name for the app dependency.'
        )
    )

    # * attribute: attribute_id
    attribute_id = StringType(
        required=True,
        metadata=dict(
            description='The attribute id for the application dependency.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The parameters for the application dependency.'
        ),
    )

# ** model: app_interface
class AppInterface(DomainObject):
    '''
    The base application interface object.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the application interface.'
        ),
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the application interface.'
        ),
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the application interface.'
        ),
    )

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path for the application instance context.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name for the application instance context.'
        ),
    )

    # * attribute: logger_id
    logger_id = StringType(
        default='default',
        metadata=dict(
            description='The logger ID for the application instance.'
        ),
    )

    # * attribute: flags
    flags = ListType(
        StringType(),
        default=['default'],
        metadata=dict(
            description='The flags for the application interface.'
        ),
    )

    # * attribute: services
    services = ListType(
        ModelType(AppServiceDependency),
        required=True,
        default=[],
        metadata=dict(
            description='The application instance service dependencies.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The application dependency constants.'
        ),
    )

    # * method: get_service
    def get_service(self, attribute_id: str) -> AppServiceDependency:
        '''
        Get the service dependency by attribute id.

        :param attribute_id: The attribute id of the service dependency.
        :type attribute_id: str
        :return: The service dependency.
        :rtype: AppServiceDependency
        '''

        # Get the service dependency by attribute id.
        return next((dep for dep in self.services if dep.attribute_id == attribute_id), None)


