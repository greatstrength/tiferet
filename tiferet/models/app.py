"""Tiferet App Models"""

# *** imports

# ** core
from typing import Any, Dict

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

    # * method: set_constants
    def set_constants(self, constants: Dict[str, Any] | None = None) -> None:
        '''
        Update the constants dictionary.

        :param constants: New constants to merge, or None to clear all. Keys with None value are removed.
        :type constants: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Clear all constants when None is provided.
        if constants is None:
            self.constants = {}

        # Otherwise merge new constants and remove keys with None value.
        else:
            self.constants.update(constants)
            self.constants = {
                key: value
                for key, value in self.constants.items()
                if value is not None
            }

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

    # * method: remove_attribute
    def remove_attribute(self, attribute_id: str) -> AppAttribute | None:
        '''
        Remove and return a dependency attribute by its attribute_id (idempotent).

        If an attribute with the given attribute_id exists, it is removed.
        If no matching attribute exists, no action is taken (silent success).

        :param attribute_id: The attribute_id of the dependency to remove.
        :type attribute_id: str
        :return: The removed AppAttribute or None.
        :rtype: AppAttribute | None
        '''

        # Iterate over attributes and remove the first match by attribute_id.
        for index, attr in enumerate(self.attributes):
            if attr.attribute_id == attribute_id:
                return self.attributes.pop(index)

        # If no attribute matches, return None without modifying the list.
        return None

    # * method: set_dependency
    def set_dependency(
        self,
        attribute_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        '''
        Set or update a dependency attribute by attribute_id (PUT semantics).

        If a dependency with the given attribute_id exists:
          - Update module_path and class_name.
          - Merge parameters (favor new values; remove keys with None value).
          - Clear parameters if parameters is None.

        If no dependency exists:
          - Create new AppAttribute and append to attributes.

        :param attribute_id: The dependency identifier.
        :type attribute_id: str
        :param module_path: The module path.
        :type module_path: str
        :param class_name: The class name.
        :type class_name: str
        :param parameters: New parameters (None to clear).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Find the existing dependency attribute by attribute_id.
        attr = self.get_attribute(attribute_id)

        # If the dependency exists, update its type fields and merge parameters.
        if attr is not None:
            attr.module_path = module_path
            attr.class_name = class_name

            # Clear parameters when parameters is None.
            if parameters is None:
                attr.parameters = {}

            # Otherwise merge and then remove keys whose value is None.
            else:
                attr.parameters.update(parameters)
                attr.parameters = {
                    key: value
                    for key, value in attr.parameters.items()
                    if value is not None
                }

        # If the dependency does not exist, create a new one and append.
        else:
            new_attr = ModelObject.new(
                AppAttribute,
                attribute_id=attribute_id,
                module_path=module_path,
                class_name=class_name,
                parameters=parameters or {},
            )
            self.attributes.append(new_attr)

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
