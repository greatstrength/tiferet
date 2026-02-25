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

# ** model: app_attribute
class AppAttribute(DomainObject):
    '''
    An app dependency attribute that defines the dependency attributes for an app interface.
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

    # * attribute: feature_flag
    feature_flag = StringType(
        default='default',
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # * attribute: data_flag
    data_flag = StringType(
        default='default',
        metadata=dict(
            description='The data flag.'
        ),
    )

    # * attribute: attributes
    attributes = ListType(
        ModelType(AppAttribute),
        required=True,
        default=[],
        metadata=dict(
            description='The application instance attributes.'
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

    # * method: get_attribute
    def get_attribute(self, attribute_id: str) -> AppAttribute:
        '''
        Get the dependency attribute by attribute id.

        :param attribute_id: The attribute id of the dependency attribute.
        :type attribute_id: str
        :return: The dependency attribute.
        :rtype: AppAttribute
        '''

        # Get the dependency attribute by attribute id.
        return next((attr for attr in self.attributes if attr.attribute_id == attribute_id), None)


