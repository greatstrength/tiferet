# *** constants

# ** constant: attributes
ATTRIBUTES = dict(

    # */ container_repo
    container_repo=dict(
        id='container_repo',
        type='data',
        dependencies=[
            dict(
                module_path='tiferet.proxies.container_yaml',
                class_name='ContainerYamlProxy',
            )
        ],
    ),

    # # */ error_repo
    error_repo=dict(
        id='error_repo',
        type='data',
        dependencies=[
            dict( 
                module_path='tiferet.proxies.error_yaml',
                class_name='ErrorYamlProxy',
            )
        ],
    ),

    # */ feature_repo
    feature_repo=dict(
        id='feature_repo',
        type='data',
        dependencies=[
            dict(
                module_path='tiferet.proxies.feature_yaml',
                class_name='FeatureYamlProxy',
            )
        ],
    ),

    # */ app_repo
    app_repo=dict(
        id='app_repo',
        type='data',
        dependencies=[
            dict(
                module_path='tiferet.proxies.app_yaml',
                class_name='AppYamlProxy',
            )
        ],
    ),

    # */ import_app_repo_cmd
    import_app_repo_cmd=dict(
        id='import_app_repo_cmd',
        type='command',
        dependencies=[
            dict(
                module_path='tiferet.commands.app',
                class_name='ImportAppRepository',
            )
        ],
    ),

    # */ list_app_interfaces_cmd
    list_app_interfaces_cmd=dict(
        id='list_app_interfaces_cmd',
        type='command',
        dependencies=[
            dict(
                module_path='tiferet.commands.app',
                class_name='ListAppInterfaces',
            )
        ],
    ),

    # /* 
)


# ** constant: constants
CONSTANTS = dict(

    # */ container_config_file
    container_config_file='app/configs/container.yml',

    # */ feature_config_file
    feature_config_file='app/configs/features.yml',

    # */ error_config_file
    error_config_file='app/configs/errors.yml',
)