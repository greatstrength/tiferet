# *** imports

# ** app
from .settings import *


# *** models

# ** model: app_dependency
class AppDependency(ValueObject):
    
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


# ** model: app_settings
class AppSettings(Entity):
    '''
    The base application interface object.
    '''

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

    # attribute: feature_flag
    feature_flag = StringType(
        default='core',
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # attribute: data_flag
    data_flag = StringType(
        metadata=dict(
            description='The data flag.'
        ),
    )

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(AppDependency),
        required=True,
        default=[],
        metadata=dict(
            description='The application interface dependencies.'
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

    def add_dependency(self, module_path: str, class_name: str, attribute_id: str):
        '''
        Add a dependency to the application interface.

        :param module_path: The module path for the app dependency.
        :type module_path: str
        :param class_name: The class name for the app dependency.
        :type class_name: str
        :param attribute_id: The attribute id for the application dependency.
        :type attribute_id: str
        :return: The added dependency.
        :rtype: AppDependency
        '''

        # Create a new AppDependency object.
        dependency = ModelObject.new(
            AppDependency,
            module_path=module_path,
            class_name=class_name,
            attribute_id=attribute_id
        )

        # Add the dependency to the list of dependencies.
        self.dependencies.append(dependency)
    
    # * method: get_dependency
    def get_dependency(self, attribute_id: str) -> AppDependency:
        '''
        Get the dependency by attribute id.

        :param attribute_id: The attribute id of the dependency.
        :type attribute_id: str
        :return: The dependency.
        :rtype: AppDependency
        '''

        # Get the dependency by attribute id.
        return next((dep for dep in self.dependencies if dep.attribute_id == attribute_id), None)
    