"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..domain import (
    AppServiceDependency,
    AppInterface,
    DomainObject,
    StringType,
    DictType,
    ModelType,
)
from ..events import RaiseError, a
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

    # * method: add_service
    def add_service(self, module_path: str, class_name: str, attribute_id: str, parameters: Dict[str, str] = {}) -> None:
        '''
        Add a service dependency to the app interface.

        :param module_path: The module path for the service dependency.
        :type module_path: str
        :param class_name: The class name for the service dependency.
        :type class_name: str
        :param attribute_id: The id for the service dependency.
        :type attribute_id: str
        :param parameters: Additional parameters for the service dependency.
        :type parameters: dict
        :return: None
        :rtype: None
        '''

        # Create a new AppServiceDependency object.
        dependency = DomainObject.new(
            AppServiceDependency,
            module_path=module_path,
            class_name=class_name,
            attribute_id=attribute_id,
            parameters=parameters,
        )

        # Add the service dependency to the list of services.
        self.services.append(dependency)

    # * method: remove_service
    def remove_service(self, attribute_id: str) -> AppServiceDependency:
        '''
        Remove and return a service dependency by its attribute_id (idempotent).

        If a service dependency with the given attribute_id exists, it is removed.
        If no matching service dependency exists, no action is taken (silent success).

        :param attribute_id: The attribute_id of the service dependency to remove.
        :type attribute_id: str
        :return: The removed AppServiceDependency or None.
        :rtype: AppServiceDependency
        '''

        # Iterate over services and remove the first match by attribute_id.
        for index, dep in enumerate(self.services):
            if dep.attribute_id == attribute_id:
                return self.services.pop(index)

        # If no service dependency matches, return None without modifying the list.
        return None

    # * method: set_service
    def set_service(
        self,
        attribute_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> None:
        '''
        Set or update a service dependency by attribute_id (PUT semantics).

        If a service dependency with the given attribute_id exists:
          - Update module_path and class_name.
          - Merge parameters (favor new values; remove keys with None value).
          - Clear parameters if parameters is None.

        If no service dependency exists:
          - Create new AppServiceDependency and append to services.

        :param attribute_id: The service dependency identifier.
        :type attribute_id: str
        :param module_path: The module path.
        :type module_path: str
        :param class_name: The class name.
        :type class_name: str
        :param parameters: New parameters (None to clear).
        :type parameters: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Find the existing service dependency by attribute_id.
        dep = self.get_service(attribute_id)

        # If the service dependency exists, update its type fields and merge parameters.
        if dep is not None:
            dep.module_path = module_path
            dep.class_name = class_name

            # Clear parameters when parameters is None.
            if parameters is None:
                dep.parameters = {}

            # Otherwise merge and then remove keys whose value is None.
            else:
                dep.parameters.update(parameters)
                dep.parameters = {
                    key: value
                    for key, value in dep.parameters.items()
                    if value is not None
                }

        # If the service dependency does not exist, create a new one and append.
        else:
            new_dep = DomainObject.new(
                AppServiceDependency,
                attribute_id=attribute_id,
                module_path=module_path,
                class_name=class_name,
                parameters=parameters or {},
            )
            self.services.append(new_dep)

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

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Update a supported scalar attribute on the app interface aggregate.

        Supported attributes: name, description, module_path, class_name,
        logger_id, flags.

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
            'flags',
        }

        # Validate the attribute name.
        if attribute not in supported:
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                message='Invalid attribute: {attribute}. Supported attributes are {supported}.',
                attribute=attribute,
                supported=', '.join(sorted(supported)),
            )

        # Specific validation for module_path and class_name.
        if attribute in {'module_path', 'class_name'}:
            if not value or not str(value).strip():
                RaiseError.execute(
                    error_code=a.const.INVALID_APP_INTERFACE_TYPE_ID,
                    message='{attribute} must be a non-empty string.',
                    attribute=attribute,
                )

        # Apply the update to the attribute.
        setattr(self, attribute, value)

        # Perform final aggregate validation.
        self.validate()


# ** mapper: app_service_dependency_yaml_object
class AppServiceDependencyYamlObject(AppServiceDependency, TransferObject):
    '''
    A YAML data representation of an app service dependency object.
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
    def map(self, attribute_id: str, **kwargs) -> AppServiceDependency:
        '''
        Maps the app service dependency data to an app service dependency object.

        :param attribute_id: The id for the app service dependency.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app service dependency object.
        :rtype: AppServiceDependency
        '''

        # Map to the app service dependency object.
        return super().map(
            AppServiceDependency,
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
            'to_model': TransferObject.deny('services', 'constants', 'module_path', 'class_name'),
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

    # * attribute: services
    services = DictType(
        ModelType(AppServiceDependencyYamlObject),
        default={},
        serialized_name='attrs',
        deserialize_from=['attrs', 'services', 'dependencies', 'attributes'],
        metadata=dict(
            description='The app instance service dependencies.'
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
            services=[dep.map(attribute_id=dep_id) for dep_id, dep in self.services.items()],
            constants=self.constants,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(app_interface: AppInterfaceAggregate, **kwargs) -> 'AppInterfaceYamlObject':
        '''
        Creates an AppInterfaceYamlObject from an AppInterfaceAggregate model.

        :param app_interface: The app interface model.
        :type app_interface: AppInterfaceAggregate
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new AppInterfaceYamlObject.
        :rtype: AppInterfaceYamlObject
        '''

        # Create a new AppInterfaceYamlObject from the model, converting
        # the services list into a dictionary keyed by attribute_id.
        return TransferObject.from_model(
            AppInterfaceYamlObject,
            app_interface,
            services={
                dep.attribute_id: TransferObject.from_model(AppServiceDependencyYamlObject, dep)
                for dep in app_interface.services
            },
            **kwargs,
        )
