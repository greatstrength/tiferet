"""Tiferet Tests for Yaml Events"""

# *** imports

# ** app
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.di.dependency_injector import DIDynamicServiceResolver
from tiferet.domain.di import ServiceRegistration
from tiferet.domain.feature import EventFeatureStep, Feature

# *** constants

# ** constant: yaml_service_registration
YAML_SERVICE_REGISTRATION = {
    'id': 'yaml_service',
    'module_path': 'tiferet.utils.yaml',
    'class_name': 'YamlLoader',
    'parameters': {},
}

# ** constant: load_yaml_registration
LOAD_YAML_REGISTRATION = {
    'id': 'LoadYaml',
    'module_path': 'tiferet.events.yaml',
    'class_name': 'LoadYaml',
    'parameters': {},
}

# *** functions

# ** function: yaml_resolver
def yaml_resolver() -> DIDynamicServiceResolver:
    '''
    Build a resolver from the YAML registrations. No path parameter.

    :return: The service resolver.
    :rtype: DIDynamicServiceResolver
    '''

    # yaml_service is registered first so the event factory can wire it.
    registrations = [
        ServiceRegistration(**YAML_SERVICE_REGISTRATION),
        ServiceRegistration(**LOAD_YAML_REGISTRATION),
    ]

    class Source:
        '''Supplies the registrations. Not a container or resolver subclass.'''

        def list_all(self):
            return registrations, {}

    return DIDynamicServiceResolver(Source())

# *** testers

# ** tester: test_yaml_registration
class TestYamlRegistration:
    '''
    One YamlLoader registration, with no path parameter, serves any path.
    '''

    # * test: one_registration_reads_any_path
    def test_one_registration_reads_any_path(self, tmp_path):
        '''
        FeatureContext runs LoadYaml once. The same registration reads a second path.
        '''

        # The service registration has no path parameter.
        assert YAML_SERVICE_REGISTRATION['module_path'] == 'tiferet.utils.yaml'
        assert YAML_SERVICE_REGISTRATION['class_name'] == 'YamlLoader'
        assert 'path' not in YAML_SERVICE_REGISTRATION['parameters']
        assert LOAD_YAML_REGISTRATION['module_path'] == 'tiferet.events.yaml'
        assert LOAD_YAML_REGISTRATION['class_name'] == 'LoadYaml'

        # Two files, one registration.
        first = tmp_path / 'first.yml'
        second = tmp_path / 'second.yml'
        first.write_text('name: first\n', encoding='utf-8')
        second.write_text('name: second\n', encoding='utf-8')
        resolver = yaml_resolver()
        feature = Feature(
            id='yaml.load',
            name='Load YAML',
            steps=[
                EventFeatureStep(
                    name='Load',
                    service_id=LOAD_YAML_REGISTRATION['id'],
                ),
            ],
        )
        context = FeatureContext.from_domain(
            feature,
            get_dependency=resolver.get_dependency,
        )
        request = RequestContext(
            data={'path': str(first)},
            feature_id='yaml.load',
        )

        # path comes from request data. The step service id is the event id.
        assert feature.steps[0].service_id == 'LoadYaml'
        context.execute_feature(request)
        assert request.result == {'name': 'first'}

        # The same registration, still with no path, reads a second path.
        service = resolver.get_dependency('yaml_service')
        assert service.path is None
        assert service.load_mapping(str(second)) == {'name': 'second'}
