"""Tiferet Tester Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .. import a
from ..assets import tester
from ..contexts.app import add_default_app_sessions
from ..contexts.cache import CacheContext
from ..contexts.tester import (
    TESTER_CACHE_PREFIX,
    TesterObject,
    add_default_testers,
)
from ..events import DomainEvent
from ..events.tester import GetTester
from . import core

# *** blueprints

# ** blueprint: build_cache
@add_default_app_sessions(a.tester.CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(a.tester.CORE_DEFAULT_TESTERS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''Build the tester-dialect cache without standard app catalogs.

    :param cache: Optional root namespace seed values.
    :type cache: Dict[str, Any] | None
    :return: The tester-scoped cache.
    :rtype: CacheContext
    '''

    # Extend the bare core cache with only tester dialect catalogs.
    return core.build_cache(cache)

# ** blueprint: resolve_tester
def resolve_tester(
        id: str,
        tester_config: str | None = None,
    ) -> TesterObject:
    '''Resolve one tester domain object from defaults or configuration.

    :param id: The tester identifier.
    :type id: str
    :param tester_config: Optional tester configuration file path.
    :type tester_config: str | None
    :return: The resolved tester domain object.
    :rtype: TesterObject
    '''

    # Build the isolated dialect cache and prefer its seeded default.
    cache = build_cache()
    tester = cache.get(id, *TESTER_CACHE_PREFIX)
    if tester is not None:
        return tester

    # Load the tester dialect session that declares its default service.
    app_session = core.get_app_session(a.tester.TIFERET_TESTER_ID, cache)

    # Apply a caller-supplied repository configuration without mutating the session.
    if tester_config is not None:
        constants = dict(app_session.constants)
        constants[a.tester.TESTER_CONFIG_ID] = tester_config
        app_session = app_session.model_copy(update={'constants': constants})

    # Compose the session's tester service through the standard app container.
    app_container = core.build_app_service_container(cache, app_session)
    tester_service = app_container.get_dependency(a.tester.TESTER_SERVICE_ID)

    # Resolve a non-default tester through its domain event and injected service.
    return DomainEvent.handle(
        GetTester,
        dependencies={
            'tester_service': tester_service,
        },
        id=id,
        default_tester_index=cache.get_by_prefix(*TESTER_CACHE_PREFIX),
    )
