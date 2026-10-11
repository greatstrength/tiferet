"""Tiferet Tests for Yaml Events"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.di.dependency_injector import DIDynamicServiceResolver
from tiferet.domain.di import ServiceRegistration
from tiferet.domain.feature import EventFeatureStep, Feature
from tiferet.events.core import DomainEvent, TiferetError
from tiferet.events.yaml import (
    LoadYaml,
    ReadAnchoredYaml,
    SaveYaml,
    WriteAnchoredYaml,
    YamlEvent,
)
from tiferet.interfaces.core import ServiceError
from tiferet.interfaces.yaml import YamlService
from tiferet.utils.yaml import YamlLoader

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

# ** function: assert_plain
def assert_plain(value) -> None:
    '''
    Assert a return value contains no PyYAML node.

    :param value: The value to walk.
    :type value: Any
    '''

    # A node module starts with yaml. Plain values do not.
    assert not type(value).__module__.startswith('yaml')
    if isinstance(value, dict):
        for item in value.values():
            assert_plain(item)
    elif isinstance(value, list):
        for item in value:
            assert_plain(item)

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

# ** tester: test_yaml_event
class TestYamlEvent:
    '''
    Tests for the YamlEvent base and the unbound loader.
    '''

    # * test: unbound_loader_is_yaml_service
    def test_unbound_loader_is_yaml_service(self):
        '''
        An omitted path constructs, and the loader is a YamlService.
        '''

        # Construct with no path.
        loader = YamlLoader()

        # The registration path stays unbound.
        assert loader.path is None
        assert isinstance(loader, YamlService)

    # * test: load_mapping_ignores_bound_path
    def test_load_mapping_ignores_bound_path(self, tmp_path):
        '''
        load_mapping reads the method path, not self.path.
        '''

        # Bind one file and write a different file for the call.
        other = tmp_path / 'other.yml'
        target = tmp_path / 'target.yml'
        other.write_text('kept: true\n', encoding='utf-8')
        target.write_text('read: true\n', encoding='utf-8')
        loader = YamlLoader(path=other)

        # The execute path wins.
        assert loader.load_mapping(str(target)) == {'read': True}
        assert loader.path == Path(other)

    # * test: concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        The four file verbs extend YamlEvent and take the shared service.
        '''

        # Assert the base and each concrete event.
        service = YamlLoader()
        assert issubclass(YamlEvent, DomainEvent)
        for event_cls in (LoadYaml, SaveYaml, ReadAnchoredYaml, WriteAnchoredYaml):
            assert issubclass(event_cls, YamlEvent)
            assert event_cls(yaml_service=service).yaml_service is service

# ** tester: test_yaml_file_events
class TestYamlFileEvents:
    '''
    Tests for the four file verbs on an unbound YamlLoader.
    '''

    # * method: handle_yaml
    def handle_yaml(self, event_cls, **kwargs):
        '''
        Run a YAML file event on an unbound loader.

        :param event_cls: The event class to handle.
        :type event_cls: type
        :param kwargs: Execute arguments.
        :type kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # The other verbs run on a loader constructed with no path.
        return DomainEvent.handle(
            event_cls,
            dependencies={'yaml_service': YamlLoader()},
            **kwargs,
        )

    # * test: missing_or_blank_path_is_required
    def test_missing_or_blank_path_is_required(self, tmp_path):
        '''
        A missing or blank required string is COMMAND_PARAMETER_REQUIRED.
        '''

        # A missing path is that error.
        with pytest.raises(TiferetError) as missing:
            self.handle_yaml(LoadYaml)
        assert missing.value.error_code == 'COMMAND_PARAMETER_REQUIRED'

        # A blank path is that error.
        with pytest.raises(TiferetError) as blank:
            self.handle_yaml(LoadYaml, path='   ')
        assert blank.value.error_code == 'COMMAND_PARAMETER_REQUIRED'

        # An empty mapping is a valid data value, not that error.
        path = tmp_path / 'empty-map.yml'
        result = self.handle_yaml(SaveYaml, path=str(path), data={})
        assert result == {}
        assert result is not None

    # * test: load_empty_and_reject_list_root
    def test_load_empty_and_reject_list_root(self, tmp_path):
        '''
        An empty file loads as {}. A list root is YAML_MAPPING_REQUIRED.
        '''

        # An empty file stays an empty mapping.
        empty = tmp_path / 'empty.yml'
        empty.write_text('', encoding='utf-8')
        assert self.handle_yaml(LoadYaml, path=str(empty)) == {}

        # A list root is not a mapping.
        listing = tmp_path / 'list.yml'
        listing.write_text('- one\n- two\n', encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            self.handle_yaml(LoadYaml, path=str(listing))
        assert exc_info.value.error_code == 'YAML_MAPPING_REQUIRED'

    # * test: missing_read_path
    def test_missing_read_path(self, tmp_path):
        '''
        A missing read path is YAML_FILE_NOT_FOUND from the service.
        '''

        # The event does not name that id. The service does.
        with pytest.raises(ServiceError) as exc_info:
            self.handle_yaml(LoadYaml, path=str(tmp_path / 'missing.yml'))
        assert exc_info.value.error_code == 'YAML_FILE_NOT_FOUND'

    # * test: save_returns_the_mapping
    def test_save_returns_the_mapping(self, tmp_path):
        '''
        SaveYaml returns the mapping it wrote, and a later load matches it.
        '''

        # Save through the event on an unbound loader.
        path = tmp_path / 'saved.yml'
        data = {'name': 'saved', 'count': 2}
        result = self.handle_yaml(SaveYaml, path=str(path), data=data)

        # The return is the given mapping, not None and not a re-read.
        assert result is data
        assert result is not None
        assert YamlLoader().load_mapping(str(path)) == data
        assert_plain(result)

    # * test: read_and_write_anchored
    def test_read_and_write_anchored(self, tmp_path):
        '''
        Anchored read returns file text and string names. A duplicate does not create a file.
        '''

        # Write anchored text through the event.
        path = tmp_path / 'anchored.yml'
        written = self.handle_yaml(
            WriteAnchoredYaml,
            path=str(path),
            text='item: &item\n  name: one\n',
        )

        # The return is text and names, not a node.
        assert written['anchors'] == ['item']
        assert all(isinstance(name, str) for name in written['anchors'])
        assert path.read_text(encoding='utf-8') == written['text']
        assert_plain(written)

        # Read returns the file text and the same names.
        read = self.handle_yaml(ReadAnchoredYaml, path=str(path))
        assert read['text'] == path.read_text(encoding='utf-8')
        assert read['anchors'] == ['item']
        assert all(isinstance(name, str) for name in read['anchors'])
        assert_plain(read)

        # A list root is legal for the anchored read.
        listing = tmp_path / 'list.yml'
        listing.write_text('- one\n- two\n', encoding='utf-8')
        listed = self.handle_yaml(ReadAnchoredYaml, path=str(listing))
        assert listed['text'] == listing.read_text(encoding='utf-8')
        assert listed['anchors'] == []
        assert_plain(listed)

        # A duplicate anchor fails before the file is created.
        conflict = tmp_path / 'conflict.yml'
        with pytest.raises(ServiceError) as exc_info:
            self.handle_yaml(
                WriteAnchoredYaml,
                path=str(conflict),
                text='a: &item 1\nb: &item 2\n',
            )
        assert exc_info.value.error_code == 'YAML_ANCHOR_CONFLICT'
        assert not conflict.exists()

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
        assert_plain(request.result)

        # The same registration, still with no path, reads a second path.
        service = resolver.get_dependency('yaml_service')
        assert service.path is None
        assert service.load_mapping(str(second)) == {'name': 'second'}
