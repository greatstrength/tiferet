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

    class Options():
        '''
        The options for the app dependency data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data.yaml': DataObject.deny('attribute_id')
        }


# ** data: app_interface_yaml_data
class AppInterfaceYamlData(AppInterface, DataObject):
    '''
    A data representation of an app interface object.
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

    # * attribute: container_context
    container_context = ModelType(
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

    # * attribute: error_context
    error_context = ModelType(
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

    # * attribute: feature_context
    feature_context = ModelType(
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
    def map(self, **kwargs) -> AppInterface:
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
            dependencies.append(self.container_repo.map(AppDependency, attribute_id='container_repo'))
        if self.container_context:
            dependencies.append(self.container_context.map(AppDependency, attribute_id='container_context'))
        if self.error_repo:
            dependencies.append(self.error_repo.map(AppDependency, attribute_id='error_repo'))
        if self.error_context:
            dependencies.append(self.error_context.map(AppDependency, attribute_id='error_context'))
        if self.feature_repo:
            dependencies.append(self.feature_repo.map(AppDependency, attribute_id='feature_repo'))
        if self.feature_context:
            dependencies.append(self.feature_context.map(AppDependency, attribute_id='feature_context'))
        if self.app_context:
            dependencies.append(self.app_context.map(AppDependency, attribute_id='app_context'))

        # Map the app interface data.
        return super().map(AppInterface,
            dependencies=dependencies,
            **self.to_primitive('to_model'),
            **kwargs
        )
