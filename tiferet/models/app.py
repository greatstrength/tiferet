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

# ** model: app_interface
class AppInterface(Entity):
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
    