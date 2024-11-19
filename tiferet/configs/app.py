# *** imports

# ** app
from ..domain.app import AppRepositoryConfiguration


# *** constants

# ** constant: APP_REPO
APP_REPO = AppRepositoryConfiguration.new(
    module_path='tiferet.repos.app',
    class_name='YamlProxy',
    params=dict(
        app_config_file='app/configs/app.yml'
    ),
)