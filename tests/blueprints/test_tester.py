"""Tiferet Tester Blueprint Tests"""

# *** imports

# ** infra
import yaml

# ** app
from tiferet import a
from tiferet.blueprints.tester import build_cache, resolve_tester
from tiferet.contexts.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.tester import TESTER_CACHE_PREFIX
from tiferet.mappers import TesterAggregate as ComponentTester

# *** tests

# ** test: tester_build_cache
def test_tester_build_cache_isolated_from_standard_app_catalogs():
    '''Test that the tester dialect seeds only tester-scoped catalog entries.'''

    # Build the tester-specific cache.
    cache = build_cache()

    # Verify tester defaults are present while standard app catalogs are absent.
    assert set(cache.get_by_prefix(*TESTER_CACHE_PREFIX)) == set(
        a.tester.CORE_DEFAULT_TESTERS,
    )
    assert cache.get_by_prefix(*ERROR_CACHE_PREFIX) == {}
    assert cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX) == {}
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == {}

# ** test: resolve_tester
def test_resolve_tester_returns_seeded_default_aggregate():
    '''Test direct resolution from the tester cache catalog.'''

    # Resolve a default tester through the non-root blueprint function.
    tester = resolve_tester('aggregate.ErrorAggregate')

    # Assert the resolved object is the expected aggregate representation.
    assert isinstance(tester, ComponentTester)
    assert tester.id == 'aggregate.ErrorAggregate'

# ** test: resolve_tester_with_config
def test_resolve_tester_uses_tester_session_service(tmp_path) -> None:
    '''Test custom configuration resolves through the tester app service.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: object
    '''

    # Write a non-default tester definition to a temporary configuration file.
    config_file = tmp_path / 'testers.yml'
    with open(config_file, 'w', encoding='utf-8') as config_stream:
        yaml.safe_dump(
            {
                'testers': {
                    'domain.Custom': {
                        'type': 'domain',
                        'module_path': 'tiferet.domain.error',
                        'class_name': 'ErrorMessage',
                        'sample_data': {},
                    },
                },
            },
            config_stream,
        )

    # Resolve the tester through the default service declared on the session.
    tester = resolve_tester('domain.Custom', tester_config=str(config_file))
    assert tester.id == 'domain.Custom'
