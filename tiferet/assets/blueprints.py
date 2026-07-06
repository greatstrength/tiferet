"""Tiferet Assets Builders

Provides the default app service class location used during application
bootstrapping. The default service wiring catalog and bootstrap constants now
live in ``assets/app.py`` as ``app.CORE_DEFAULT_SERVICES`` and
``app.CORE_DEFAULT_CONSTANTS``.
"""

# *** constants

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH: str = 'tiferet.repos.app'

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME: str = 'AppConfigRepository'
