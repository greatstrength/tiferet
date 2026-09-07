"""Tiferet Tester Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .. import a
from ..assets import TiferetError, tester
from ..contexts.app import add_default_app_sessions
from ..contexts.cache import CacheContext
from ..contexts.tester import TESTER_CACHE_PREFIX, add_default_testers
from ..events import DomainEvent
from ..events.tester import GetTester
from ..mappers import TesterAggregate
from ..repos.tester import TesterConfigRepository
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
    ) -> TesterAggregate:
    '''Resolve one tester aggregate from defaults or configuration.

    :param id: The tester identifier.
    :type id: str
    :param tester_config: Optional tester configuration file path.
    :type tester_config: str | None
    :return: The resolved tester aggregate.
    :rtype: TesterAggregate
    '''

    # Build the isolated dialect cache and prefer its seeded default.
    cache = build_cache()
    tester_aggregate = cache.get(id, *TESTER_CACHE_PREFIX)
    if tester_aggregate is not None:
        return tester_aggregate

    # Report a miss immediately when no config source was supplied.
    if tester_config is None:
        TiferetError.raise_error(
            a.error.TESTER_NOT_FOUND_ID,
            f'Tester not found: {id}.',
            id=id,
        )

    # Resolve a non-default tester through its domain event and config service.
    return DomainEvent.handle(
        GetTester,
        dependencies={
            'tester_service': TesterConfigRepository(tester_config),
        },
        id=id,
        default_tester_index=cache.get_by_prefix(*TESTER_CACHE_PREFIX),
    )
