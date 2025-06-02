# *** imports

# ** app
from .settings import *
from ..models.app import *


# *** data

# ** data: app_dependency_yaml_data
class AppDependencyYamlData(AppDependency, DataObject):
    '''
    A YAML data representation of an app dependency object.
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
    def map(self, **kwargs) -> AppDependency:
        '''
        Maps the app dependency data to an app dependency object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app dependency object.
        :rtype: AppDependency
        '''

        # Map to the app dependency object.
        return super().map(
            AppDependency,
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )


# ** data: app_interface_yaml_data
class AppSettingsYamlData(AppSettings, DataObject):
    '''
    A data representation of an app settings object.
    '''

    class Options():
        '''
        The options for the app interface data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('dependencies'),
            'to_data': DataObject.deny('id')
        }

    # * attribute: container_repo
    container_repo = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The container repository dependency settings.'
        ),
    )

    # * attribute: container_service
    container_service = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The container context dependency settings.'
        ),
    )

    # * attribute: error_repo
    error_repo = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The error repository dependency settings.'
        ),
    )

    # * attribute: error_service
    error_service = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The error context dependency settings.'
        ),
    )

    # * attribute: feature_repo
    feature_repo = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The feature repository dependency settings.'
        ),
    )

    # * attribute: feature_service
    feature_service = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The feature context dependency settings.'
        ),
    )

    # * attribute: dependencies
    app_context = ModelType(
        AppDependencyYamlData,
        metadata=dict(
            description='The app interface context dependency settings.'
        ),
    )

    # * method: map
    def map(self, **kwargs) -> AppSettings:
        '''
        Maps the app interface data to an app interface object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new app interface object.
        :rtype: AppInterface
        '''

        # Create the dependencies list.
        dependencies = []

        # Add the dependencies to the list if they are not None.
        if self.container_repo:
            dependencies.append(self.container_repo.map(attribute_id='container_repo'))
        if self.container_service:
            dependencies.append(self.container_service.map(attribute_id='container_service'))
        if self.error_repo:
            dependencies.append(self.error_repo.map(attribute_id='error_repo'))
        if self.error_service:
            dependencies.append(self.error_service.map(attribute_id='error_service'))
        if self.feature_repo:
            dependencies.append(self.feature_repo.map(attribute_id='feature_repo'))
        if self.feature_service:
            dependencies.append(self.feature_service.map(attribute_id='feature_service'))
        if self.app_context:
            dependencies.append(self.app_context.map(attribute_id='app_context'))

        # Map the app interface data.
        return super().map(AppSettings,
            dependencies=dependencies,
            **self.to_primitive('to_model'),
            **kwargs
        )
