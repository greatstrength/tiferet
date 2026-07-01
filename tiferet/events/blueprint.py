"""Tiferet Blueprint Domain Events"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .settings import DomainEvent, a
from .static import ParseParameter
from ..domain import AppInterface, ServiceRegistration
from ..di import ServiceResolver, injectable_parameter_names

# *** events

# ** event: create_service_resolver
class CreateServiceResolver(DomainEvent):
    '''
    A bootstrap domain event that composes a fully wired ServiceResolver from
    an application interface definition. It locates the DI repository
    dependency declared on the interface, constructs it, and injects the real
    parameter parser so the DI layer never imports the event itself.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['app_interface'])
    def execute(self,
            app_interface: AppInterface,
            default_configurations: List[Dict[str, Any]] = None,
            default_constants: Dict[str, Any] = None,
            **kwargs,
        ) -> ServiceResolver:
        '''
        Compose a ServiceResolver from the app interface's DI repository dependency.

        :param app_interface: The resolved application interface definition.
        :type app_interface: AppInterface
        :param default_configurations: Optional raw default service configuration dicts,
            validated into a typed default-config index merged beneath the repository.
        :type default_configurations: List[Dict[str, Any]] | None
        :param default_constants: Optional default DI constants merged at lower priority.
        :type default_constants: Dict[str, Any] | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A fully wired ServiceResolver.
        :rtype: ServiceResolver
        '''

        # Locate the DI repository dependency declared on the interface.
        dependency = app_interface.get_service('di_service')

        # Verify the DI service dependency is present; this error lives at the
        # event layer, which has assets access.
        self.verify(
            dependency is not None,
            a.const.DI_SERVICE_NOT_CONFIGURED_ID,
            interface_id=app_interface.id,
        )

        # Resolve the DI repository type from the dependency.
        di_repo_type = dependency.get_service_type()

        # Filter the merged interface constants and dependency parameters to the
        # repository's injectable constructor parameters (e.g. di_config).
        injectable = injectable_parameter_names(di_repo_type)
        merged = {**(app_interface.constants or {}), **(dependency.parameters or {})}
        ctor_kwargs = {key: value for key, value in merged.items() if key in injectable}

        # Construct the DI repository. These constructor kwargs are literal
        # configuration values (e.g. di_config paths) passed verbatim, not routed
        # through ParseParameter; env-style references are not expected here.
        di_service = di_repo_type(**ctor_kwargs)

        # Build the typed default service configuration index keyed by id.
        default_config_index = {
            config.id: config
            for config in (
                ServiceRegistration.model_validate(data)
                for data in (default_configurations or [])
            )
        }

        # Compose and return the resolver, injecting the real parameter parser.
        return ServiceResolver(
            di_service=di_service,
            parse_parameter=ParseParameter.execute,
            default_config_index=default_config_index,
            default_di_constants=default_constants or {},
        )
