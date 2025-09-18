# *** imports

# ** app
from .settings import *
from ..models.app import *
from ..contracts.app import AppAttribute as AppAttributeContract
from ..contracts.app import AppInterface as AppInterfaceContract


# *** data

# ** data: app_attribute_yaml_data
class AppAttributeYamlData(AppAttribute, DataObject):
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
            'to_model': DataObject.deny('parameters', 'attribute_id'),
            'to_data.yaml': DataObject.deny('attribute_id')
        }

    # * method: map
    def map(self, attribute_id: str, **kwargs) -> AppAttributeContract:
        '''
        Maps the app dependency data to an app dependency object.

        :param attribute_id: The id for the app dependency attribute.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app attribute dependency contract.
        :rtype: AppAttributeContract
        '''

        # Map to the app dependency object.
        return super().map(
            AppAttribute,
            attribute_id=attribute_id,
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )


# ** data: app_interface_yaml_data
class AppInterfaceYamlData(AppInterface, DataObject):
    '''
    A data representation of an app interface settings object.
    '''

    class Options():
        '''
        The options for the app interface data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('attributes', 'constants', 'module_path', 'class_name'),
            'to_data.yaml': DataObject.deny('id')
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
        ModelType(AppAttributeYamlData),
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
    def map(self, **kwargs) -> AppInterfaceContract:
        '''
        Maps the app interface data to an app interface contract.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app interface contract.
        :rtype: AppInterfaceContract
        '''

        # Map the app interface data.
        return super().map(AppInterface,
            module_path=self.module_path,
            class_name=self.class_name,
            attributes=[attr.map(attribute_id=attr_id) for attr_id, attr in self.attributes.items()],
            constants=self.constants,
            **self.to_primitive('to_model'),
            **kwargs
        )