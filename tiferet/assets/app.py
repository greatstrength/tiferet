"""Tiferet Assets App

Provides the default interface definition for the built-in Tiferet CLI
management application.
"""

# *** configs

# ** config: default_tiferet_app_interface
DEFAULT_TIFERET_APP_INTERFACE = dict(
    id='tiferet_app',
    name='Tiferet App',
    description='Default built-in application interface',
    module_path='tiferet.contexts.app',
    class_name='AppInterfaceContext',
)

# ** config: default_tiferet_cli_interface
DEFAULT_TIFERET_CLI_INTERFACE = dict(
    id='tiferet_cli',
    name='Tiferet CLI',
    description='Built-in CLI for managing Tiferet application configurations',
    module_path='tiferet.contexts.app',
    class_name='AppInterfaceContext',
)
