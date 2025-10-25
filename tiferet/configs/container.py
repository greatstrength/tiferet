# *** imports

# ** app
from ...app.domain.container import ContainerAttribute, ContainerDependency


# *** configs (container_attribute)

# ** config: feature_repo
feature_repo = ContainerAttribute.new(
    id='feature_repo',
    type='data',
    flags=[
        ContainerDependency.new(
            flag='yaml',
            module_path='app.repositories.feature',
            class_name='YamlProxy',
            parameters={
                'feature_config_file': 'app/configs/features.yml'
            }
        )
    ]
)

# ** config: error_repo
error_repo = ContainerAttribute.new(
    id='error_repo',
    type='data',
    flags=[
        ContainerDependency.new(
            flag='yaml',
            module_path='app.repositories.error',
            class_name='YamlProxy',
            parameters={
                'error_config_file': 'app/configs/errors.yml'
            }
        )
    ]
)

# ** config: set_container_attribute
set_container_attribute = ContainerAttribute.new(
    id='set_container_attribute',
    type='feature',
    flags=[
        ContainerDependency.new(
            flag='core',
            module_path='app.commands.container',
            class_name='SetContainerAttribute'
        )
    ]
)

# ** config: add_new_feature
add_new_feature = ContainerAttribute.new(
    id='add_new_feature',
    type='feature',
    flags=[
        ContainerDependency.new(
            flag='core',
            module_path='app.commands.feature',
            class_name='AddNewFeature'
        )
    ]
)

# ** config: add_feature_command
add_feature_command = ContainerAttribute.new(
    id='add_feature_command',
    type='feature',
    flags=[
        ContainerDependency.new(
            flag='core',
            module_path='app.commands.feature',
            class_name='AddFeatureCommand'
        )
    ]
)

# ** config: add_new_error
add_new_error = ContainerAttribute.new(
    id='add_new_error',
    type='feature',
    flags=[
        ContainerDependency.new(
            flag='core',
            module_path='app.commands.error',
            class_name='AddNewError'
        )
    ]
)