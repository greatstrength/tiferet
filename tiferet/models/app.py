"""Tiferet App Models"""

# *** imports

# ** core
from typing import Any

# ** app
from .settings import (
    ModelObject,
    StringType,
    ListType,
    DictType,
    ModelType,
)
from ..commands.static import RaiseError
from ..commands.settings import const

# *** models

# ** model: app_attribute
class AppAttribute(ModelObject):
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
class AppInterface(ModelObject):
    '''
    The base application interface object.
    '''

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

    # * logger_id
    logger_id = StringType(
        default='default',
        metadata=dict(
            description='The logger ID for the application instance.'
        ),
    )

    # attribute: feature_flag
    feature_flag = StringType(
        default='default',
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # attribute: data_flag
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

    # * method: add_attribute
    def add_attribute(self, module_path: str, class_name: str, attribute_id: str):
        '''
        Add a dependency attribute to the app interface.

        :param module_path: The module path for the app dependency attribute.
        :type module_path: str
        :param class_name: The class name for the app dependency attribute.
        :type class_name: str
        :param attribute_id: The id for the app dependency attribute.
        :type attribute_id: str
        :return: The added dependency.
        :rtype: AppDependency
        '''

        # Create a new AppDependency object.
        dependency = ModelObject.new(
            AppAttribute,
            module_path=module_path,
            class_name=class_name,
            attribute_id=attribute_id
        )

        # Add the dependency to the list of dependencies.
        self.attributes.append(dependency)

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

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Update a supported scalar attribute on the app interface.

        Supported attributes: name, description, module_path, class_name,
        logger_id, feature_flag, data_flag.

        :param attribute: The attribute name to update.
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Define the set of supported attributes.
        supported = {
            'name',
            'description',
            'module_path',
            'class_name',
            'logger_id',
            'feature_flag',
            'data_flag',
        }

        # Validate the attribute name.
        if attribute not in supported:
            RaiseError.execute(
                error_code=const.INVALID_MODEL_ATTRIBUTE_ID,
                message='Invalid attribute: {attribute}. Supported attributes are {supported}.',
                attribute=attribute,
                supported=', '.join(sorted(supported)),
            )

        # Specific validation for module_path and class_name.
        if attribute in {'module_path', 'class_name'}:
            if not value or not str(value).strip():
                RaiseError.execute(
                    error_code=const.INVALID_APP_INTERFACE_TYPE_ID,
                    message='{attribute} must be a non-empty string.',
                    attribute=attribute,
                )

        # Apply the update to the attribute.
        setattr(self, attribute, value)

        # Perform final model validation.
        self.validate()
