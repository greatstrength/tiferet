"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..entities import (
    AppAttribute,
    AppInterface,
    StringType,
    DictType,
    ModelType,
)
from .settings import (
    Aggregate,
    TransferObject,
    DEFAULT_MODULE_PATH,
    DEFAULT_CLASS_NAME
)

# *** mappers

# ** mapper: app_interface_aggregate
class AppInterfaceAggregate(AppInterface, Aggregate):
    '''
    An aggregate representation of an app interface contract.
    '''

    # * method: new
    @staticmethod
    def new(
        app_interface_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'AppInterfaceAggregate':
        '''
        Initializes a new app interface aggregate.

        :param app_interface_data: The data to create the app interface aggregate from.
        :type app_interface_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new app interface aggregate.
        :rtype: AppInterfaceAggregate
        '''

        # Create a new app interface aggregate from the provided app interface contract.
        return Aggregate.new(
            AppInterfaceAggregate,
            validate=validate,
            strict=strict,
            **app_interface_data,
            **kwargs
        )


# ** mapper: app_attribute_yaml_object
class AppAttributeYamlObject(AppAttribute, TransferObject):
    '''
    A YAML data representation of an app dependency attribute object.
    '''

    # * attribute: attribute_id
    attribute_id = StringType(
        metadata=dict(
            description='The attribute id for the application dependency that is not required for assembly.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        serialized_name='params',
        deserialize_from=['params', 'parameters'],
        metadata=dict(
            description='The parameters for the application dependency that are not required for assembly.'
        ),
    )

    class Options():
        '''
        The options for the app dependency data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('parameters', 'attribute_id'),
            'to_data.yaml': TransferObject.deny('attribute_id'),
            'to_data.json': TransferObject.deny('attribute_id'),
        }

    # * method: map
    def map(self, attribute_id: str, **kwargs) -> AppAttribute:
        '''
        Maps the app dependency data to an app dependency object.

        :param attribute_id: The id for the app dependency attribute.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app attribute dependency object.
        :rtype: AppAttribute
        '''

        # Map to the app dependency object.
        return super().map(
            AppAttribute,
            attribute_id=attribute_id,
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )

# ** mapper: app_interface_yaml_object
class AppInterfaceYamlObject(AppInterface, TransferObject):
    '''
    A YAML data representation of an app interface settings object.
    '''

    class Options():
        '''
        The options for the app interface data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('attributes', 'constants', 'module_path', 'class_name'),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id'),
        }

    # * attribute: module_path
    module_path = StringType(
        default=DEFAULT_MODULE_PATH,
        serialized_name='module',
        deserialize_from=['module_path', 'module'],
        metadata=dict(
            description='The app context module path for the app settings.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        default=DEFAULT_CLASS_NAME,
        serialized_name='class',
        deserialize_from=['class_name', 'class'],
        metadata=dict(
            description='The class name for the app context.'
        ),
    )

    # * attribute: attributes
    attributes = DictType(
        ModelType(AppAttributeYamlObject),
        default={},
        serialized_name='attrs',
        deserialize_from=['attrs', 'attributes'],
        metadata=dict(
            description='The app instance attributes.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType,
        default={},
        serialized_name='const',
        deserialize_from=['constants', 'const'],
        metadata=dict(
            description='The constants for the app settings.'
        ),
    )

    # * method: map
    def map(self, **kwargs) -> AppInterfaceAggregate:
        '''
        Maps the app interface data to an app interface aggregate.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app interface aggregate.
        :rtype: AppInterfaceAggregate
        '''

        # Map the app interface data.
        return super().map(
            AppInterfaceAggregate,
            module_path=self.module_path,
            class_name=self.class_name,
            attributes=[attr.map(attribute_id=attr_id) for attr_id, attr in self.attributes.items()],
            constants=self.constants,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(app_interface: AppInterface, **kwargs) -> 'AppInterfaceYamlObject':
        '''
        Creates an AppInterfaceYamlObject from an AppInterface model.

        :param app_interface: The app interface model.
        :type app_interface: AppInterface
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceYamlObject.
        :rtype: AppInterfaceYamlObject
        '''

        # Create a new AppInterfaceYamlObject from the model, converting
        # the attributes list into a dictionary keyed by attribute_id.
        return TransferObject.from_model(
            AppInterfaceYamlObject,
            app_interface,
            attributes={
                attr.attribute_id: TransferObject.from_model(AppAttributeYamlObject, attr)
                for attr in app_interface.attributes
            },
            **kwargs,
        )
