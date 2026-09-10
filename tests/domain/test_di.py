"""Tests for Tiferet Domain DI"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.core import ServiceDependency
from tiferet.domain.di import (
    FlaggedDependency,
    ServiceRegistration,
)

# *** classes

# ** class: dummy_dependency
class DummyDependency:
    '''
    A stub dependency class for testing.
    '''

    pass

# ** class: dummy_dependency_alpha
class DummyDependencyAlpha(DummyDependency):
    '''
    A stub alpha dependency class for testing.
    '''

    pass

# ** class: dummy_dependency_beta
class DummyDependencyBeta(DummyDependency):
    '''
    A stub beta dependency class for testing.
    '''

    pass

# *** constants

# ** constant: flagged_dependency_sample_data
FLAGGED_DEPENDENCY_SAMPLE_DATA = {
    'flag': 'test_alpha',
    'module_path': 'tests.domain.test_di',
    'class_name': 'DummyDependencyAlpha',
    'parameters': {'test_param': 'test_value', 'param': 'value1'},
}

# ** constant: flagged_dependency_beta_sample_data
FLAGGED_DEPENDENCY_BETA_SAMPLE_DATA = {
    'flag': 'test_beta',
    'module_path': 'tests.domain.test_di',
    'class_name': 'DummyDependencyBeta',
    'parameters': {'test_param': 'test_value', 'param': 'value2'},
}

# ** constant: service_registration_sample_data
SERVICE_REGISTRATION_SAMPLE_DATA = {
    'id': 'test_service',
    'module_path': 'tests.domain.test_di',
    'class_name': 'DummyDependency',
    'dependencies': [FLAGGED_DEPENDENCY_SAMPLE_DATA],
}

# ** constant: service_registration_no_default_sample_data
SERVICE_REGISTRATION_NO_DEFAULT_SAMPLE_DATA = {
    'id': 'test_service_no_default',
    'dependencies': [FLAGGED_DEPENDENCY_SAMPLE_DATA],
}

# ** constant: service_registration_multi_sample_data
SERVICE_REGISTRATION_MULTI_SAMPLE_DATA = {
    'id': 'test_service_multi',
    'module_path': 'tests.domain.test_di',
    'class_name': 'DummyDependency',
    'dependencies': [
        FLAGGED_DEPENDENCY_SAMPLE_DATA,
        FLAGGED_DEPENDENCY_BETA_SAMPLE_DATA,
    ],
}

# *** testers

# ** tester: test_flagged_dependency
@use_tester(
    type='domain',
    target_cls=FlaggedDependency,
    sample_data=FLAGGED_DEPENDENCY_SAMPLE_DATA,
    equality_fields=['flag', 'module_path', 'class_name', 'parameters'],
)
class TestFlaggedDependency:
    '''Tests for FlaggedDependency construction.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify FlaggedDependency construction against declared sample data.'''

        test_ctx.assert_new()

# ** tester: test_service_registration
@use_tester(
    type='domain',
    target_cls=ServiceRegistration,
    sample_data=SERVICE_REGISTRATION_SAMPLE_DATA,
    equality_fields=['id', 'module_path', 'class_name'],
    description_cases=[
        ('get_dependency', ('invalid',), None),
    ],
)
class TestServiceRegistration:
    '''Tests for ServiceRegistration construction, lookup, and type resolution.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify ServiceRegistration construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify get_dependency returns None for an unknown flag.'''

        test_ctx.assert_description()

    # * test: get_dependency
    def test_get_dependency(self, test_ctx) -> None:
        '''Test successful retrieval of a flagged dependency by flag.'''

        service_registration = test_ctx.make_target()
        dep = service_registration.get_dependency('test_alpha')

        assert dep.flag == 'test_alpha'
        assert dep.module_path == 'tests.domain.test_di'
        assert dep.class_name == 'DummyDependencyAlpha'
        assert dep.parameters == {'test_param': 'test_value', 'param': 'value1'}

    # * test: get_dependency_multiple_flags
    def test_get_dependency_multiple_flags(self, test_ctx) -> None:
        '''Test priority order: first matching flag in the argument tuple wins.'''

        service_registration = test_ctx.make_target(
            data=SERVICE_REGISTRATION_MULTI_SAMPLE_DATA,
        )

        dep_alpha_first = service_registration.get_dependency('test_alpha', 'test_beta')
        assert dep_alpha_first.flag == 'test_alpha'
        assert dep_alpha_first.class_name == 'DummyDependencyAlpha'

        dep_beta_first = service_registration.get_dependency('test_beta', 'test_alpha')
        assert dep_beta_first.flag == 'test_beta'
        assert dep_beta_first.class_name == 'DummyDependencyBeta'

    # * test: get_service_type_default
    def test_get_service_type_default(self, test_ctx) -> None:
        '''Test that get_service_type returns the default type when no flags match.'''

        resolved = test_ctx.make_target().get_service_type()

        assert resolved.__qualname__ == DummyDependency.__qualname__

    # * test: get_service_type_flagged
    def test_get_service_type_flagged(self, test_ctx) -> None:
        '''Test that get_service_type resolves the flagged type when a matching flag is provided.'''

        resolved = test_ctx.make_target().get_service_type('test_alpha')

        assert resolved.__qualname__ == DummyDependencyAlpha.__qualname__

    # * test: get_service_type_no_match
    def test_get_service_type_no_match(self, test_ctx) -> None:
        '''Test that get_service_type returns None when no flag matches and there is no default.'''

        resolved = test_ctx.make_target(
            data=SERVICE_REGISTRATION_NO_DEFAULT_SAMPLE_DATA,
        ).get_service_type('unknown_flag')

        assert resolved is None

    # * test: get_service_type_flag_priority
    def test_get_service_type_flag_priority(self, test_ctx) -> None:
        '''Test that get_service_type respects flag priority order.'''

        service_registration = test_ctx.make_target(
            data=SERVICE_REGISTRATION_MULTI_SAMPLE_DATA,
        )

        resolved = service_registration.get_service_type('test_alpha', 'test_beta')
        assert resolved.__qualname__ == DummyDependencyAlpha.__qualname__

        resolved = service_registration.get_service_type('test_beta', 'test_alpha')
        assert resolved.__qualname__ == DummyDependencyBeta.__qualname__

    # * test: resolve_service_flagged
    def test_resolve_service_flagged(self, test_ctx) -> None:
        '''Test that resolve_service returns the flagged dependency's effective definition.'''

        dependency = test_ctx.make_target().resolve_service('test_alpha')

        assert isinstance(dependency, ServiceDependency)
        assert dependency.module_path == 'tests.domain.test_di'
        assert dependency.class_name == 'DummyDependencyAlpha'
        assert dependency.parameters == {'test_param': 'test_value', 'param': 'value1'}

    # * test: resolve_service_default
    def test_resolve_service_default(self, test_ctx) -> None:
        '''Test that resolve_service falls back to the registration's default definition.'''

        dependency = test_ctx.make_target().resolve_service()

        assert isinstance(dependency, ServiceDependency)
        assert dependency.module_path == 'tests.domain.test_di'
        assert dependency.class_name == 'DummyDependency'

    # * test: resolve_service_none
    def test_resolve_service_none(self, test_ctx) -> None:
        '''Test that resolve_service returns None when no flag matches and there is no default.'''

        dependency = test_ctx.make_target(
            data=SERVICE_REGISTRATION_NO_DEFAULT_SAMPLE_DATA,
        ).resolve_service('unknown_flag')

        assert dependency is None

    # * test: resolve_service_default_parameter_carry_through
    def test_resolve_service_default_parameter_carry_through(self, test_ctx) -> None:
        '''Test that resolve_service carries the registration's default parameters through.'''

        registration = test_ctx.make_target(
            data={
                'id': 'param_service',
                'module_path': 'tests.domain.test_di',
                'class_name': 'DummyDependency',
                'parameters': {'p': 'v'},
            },
        )
        dependency = registration.resolve_service()

        assert dependency.parameters == {'p': 'v'}
