"""Tiferet CLI Blueprints"""

# *** imports

# ** core
from typing import Any, List, Optional

# ** app
from .. import assets as a
from .main import (
    resolve_interface,
    realize_interface,
)

# *** blueprints

# ** blueprint: build_app
def build_app(
    interface_id: str,
    argv: Optional[List[str]] = None,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters
) -> Any:
    '''
    Build the CLI application context and dispatch argv through its CLI pipeline.

    Resolves the interface definition, realizes the configured context (which
    must be a ``CliContext`` to expose ``run_cli``), and delegates argument
    parsing, feature dispatch, exit-code handling (2 on parse failure, 1 on a
    ``TiferetAPIError``), and response printing to ``CliContext.run_cli``.
    Consumer CLI interfaces opt in by pointing their interface config at
    ``tiferet.contexts.cli`` / ``CliContext``.

    :param interface_id: The CLI interface identifier.
    :type interface_id: str
    :param argv: Optional argument list; defaults to ``sys.argv[1:]`` when None.
    :type argv: Optional[List[str]]
    :param module_path: The module path of the app service implementation.
    :type module_path: str
    :param class_name: The class name of the app service implementation.
    :type class_name: str
    :param parameters: Additional parameters to pass to the app service constructor.
    :type parameters: dict
    :return: The response from the feature execution.
    :rtype: Any
    '''

    # Resolve the session definition in a single pass.
    app_session, _ = resolve_interface(
        interface_id, module_path, class_name, **parameters)

    # Realize the CLI session context from the resolved definition.
    cli_context = realize_interface(app_session, interface_id)

    # Delegate parsing, dispatch, exit codes, and response printing to the context.
    return cli_context.run_cli(argv)
