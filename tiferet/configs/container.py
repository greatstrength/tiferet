"""Tiferet Container Configurations"""

# *** imports

# *** configs

# ** config: feature_repo
feature_repo = {
    'id': 'feature_repo',
    'type': 'data',
    'flags': [
        {
            'flag': 'yaml',
            'module_path': 'app.repositories.feature',
            'class_name': 'YamlProxy',
            'parameters': {
                'feature_config_file': 'app/configs/features.yml'
            }
        }
    ]
}

# ** config: error_repo
error_repo = {
    'id': 'error_repo',
    'type': 'data',
    'flags': [
        {
            'flag': 'yaml',
            'module_path': 'app.repositories.error',
            'class_name': 'YamlProxy',
            'parameters': {
                'error_config_file': 'app/configs/errors.yml'
            }
        }
    ]
}

# ** config: set_container_attribute
set_container_attribute = {
    'id': 'set_container_attribute',
    'type': 'feature',
    'flags': [
        {
            'flag': 'core',
            'module_path': 'app.commands.container',
            'class_name': 'SetContainerAttribute'
        }
    ]
}

# ** config: add_new_feature
add_new_feature = {
    'id': 'add_new_feature',
    'type': 'feature',
    'flags': [
        {
            'flag': 'core',
            'module_path': 'app.commands.feature',
            'class_name': 'AddNewFeature'
        }
    ]
}

# ** config: add_feature_command
add_feature_command = {
    'id': 'add_feature_command',
    'type': 'feature',
    'flags': [
        {
            'flag': 'core',
            'module_path': 'app.commands.feature',
            'class_name': 'AddFeatureCommand'
        }
    ]
}

# ** config: add_new_error
add_new_error = {
    'id': 'add_new_error',
    'type': 'feature',
    'flags': [
        {
            'flag': 'core',
            'module_path': 'app.commands.error',
            'class_name': 'AddNewError'
        }
    ]
}