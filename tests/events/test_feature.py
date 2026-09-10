"""Tiferet Tests for Feature Events"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.feature import (
    FeatureEvent,
    AddFeature,
    GetFeature,
    ListFeatures,
    RemoveFeature,
    UpdateFeature,
    AddFeatureStep,
    UpdateFeatureStep,
    RemoveFeatureStep,
    ReorderFeatureStep,
)
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.domain import Feature
from tiferet.interfaces import FeatureService
from tiferet.mappers import FeatureAggregate
from tiferet.blueprints.tester import use_tester

# *** functions

# ** function: populate_three_steps
def _populate_three_steps(sample_feature):
    '''
    Pre-populate a feature with three ordered steps.

    :param sample_feature: The feature aggregate to populate.
    :type sample_feature: FeatureAggregate
    :return: The three added steps.
    :rtype: tuple
    '''

    # Add three ordered steps used by reorder tests.
    first = sample_feature.add_step(
        name='first',
        service_id='container.first',
        parameters={'index': 0},
        data_key='first_key',
    )
    second = sample_feature.add_step(
        name='second',
        service_id='container.second',
        parameters={'index': 1},
        data_key='second_key',
    )
    third = sample_feature.add_step(
        name='third',
        service_id='container.third',
        parameters={'index': 2},
        data_key='third_key',
    )
    return first, second, third

# *** fixtures

# ** fixture: sample_feature
@pytest.fixture
def sample_feature() -> Feature:
    '''
    A sample Feature instance for testing.

    :return: A FeatureAggregate instance.
    :rtype: FeatureAggregate
    '''

    # Create a sample feature aggregate.
    return FeatureAggregate(
        id='group.sample_feature',
        name='Sample Feature',
        group_id='group',
        feature_key='sample_feature',
        description='A sample feature for testing.',
    )

# *** testers

# ** tester: test_feature_event
class TestFeatureEvent:
    '''
    Tests for the FeatureEvent base event shared by all feature events.
    '''

    # * test: base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that FeatureEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(FeatureEvent, DomainEvent)

    # * test: concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete feature event extends FeatureEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            AddFeature,
            GetFeature,
            ListFeatures,
            RemoveFeature,
            UpdateFeature,
            AddFeatureStep,
            UpdateFeatureStep,
            RemoveFeatureStep,
            ReorderFeatureStep,
        ):
            assert issubclass(event_cls, FeatureEvent)

    # * test: service_injection
    def test_service_injection(self):
        '''
        Test that constructing a feature event wires the shared service attribute.
        '''

        # Create a mock feature service.
        service = mock.Mock(spec=FeatureService)

        # Assert the base and a concrete event both expose the injected service.
        assert FeatureEvent(feature_service=service).feature_service is service
        assert AddFeature(feature_service=service).feature_service is service

# ** tester: test_add_feature
@use_tester(
    type='domain_event',
    target_cls=AddFeature,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        name='New Feature',
        group_id='group',
    ),
    required_params=['name', 'group_id'],
)
class TestAddFeature:
    '''
    Tests for AddFeature using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure exists to return False.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.exists.return_value = False
        return {'feature_service': service}

    # * test: minimal_success
    def test_minimal_success(self, test_ctx, mock_dependencies):
        '''
        Test successful creation of a feature with minimal required parameters.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the feature was created with derived values.
        assert isinstance(result, Feature)
        assert result.name == 'New Feature'
        assert result.group_id == 'group'
        assert result.feature_key == 'new_feature'
        assert result.id == 'group.new_feature'
        assert result.description == 'New Feature'

        # Assert the service was called correctly.
        mock_dependencies['feature_service'].exists.assert_called_once_with(result.id)
        mock_dependencies['feature_service'].save.assert_called_once_with(result)

    # * test: full_parameters
    def test_full_parameters(self, test_ctx, mock_dependencies):
        '''
        Test creation of a feature when all optional parameters are provided.
        '''

        # Execute with all parameters.
        result = test_ctx.handle(
            mock_dependencies,
            name='Explicit Feature',
            group_id='group',
            feature_key='explicit_key',
            id='group.explicit_key',
            description='Explicit description.',
            steps=[],
            log_params={'foo': 'bar'},
        )

        # Assert explicit values are used.
        assert result.name == 'Explicit Feature'
        assert result.group_id == 'group'
        assert result.feature_key == 'explicit_key'
        assert result.id == 'group.explicit_key'
        assert result.description == 'Explicit description.'
        assert result.steps == []
        assert result.log_params == {'foo': 'bar'}

        # Assert the service was called correctly.
        mock_dependencies['feature_service'].exists.assert_called_once_with(result.id)
        mock_dependencies['feature_service'].save.assert_called_once_with(result)

    # * test: duplicate_id
    def test_duplicate_id(self, test_ctx, mock_dependencies):
        '''
        Test that adding a feature with an existing ID raises FEATURE_ALREADY_EXISTS.
        '''

        # Configure the service to report the ID already exists.
        mock_dependencies['feature_service'].exists.return_value = True

        # Execute and expect a FEATURE_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.FEATURE_ALREADY_EXISTS_ID

        # Verify the feature was not saved.
        mock_dependencies['feature_service'].exists.assert_called_once()
        mock_dependencies['feature_service'].save.assert_not_called()

    # * test: contextual_kwargs_not_forwarded
    def test_contextual_kwargs_not_forwarded(self, test_ctx, mock_dependencies):
        '''
        Test that contextual pipeline kwargs are not forwarded into FeatureAggregate.

        FeatureAggregate forbids unknown fields, so a clean creation confirms
        the extra kwargs are dropped rather than forwarded.
        '''

        # Execute with extra contextual kwargs that are not Feature fields.
        result = test_ctx.handle(mock_dependencies, request=object(), logger=object())

        # Assert the feature was created without error and ignored the extra kwargs.
        assert isinstance(result, Feature)
        assert result.name == 'New Feature'
        assert not hasattr(result, 'request')
        mock_dependencies['feature_service'].save.assert_called_once_with(result)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: test_get_feature
@use_tester(
    type='service_event',
    target_cls=GetFeature,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(id='group.sample_feature'),
    required_params=['id'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
)
class TestGetFeature:
    '''
    Tests for GetFeature using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test successful retrieval of a feature.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the feature is returned.
        assert result is sample_feature
        mock_dependencies['feature_service'].get.assert_called_once_with('group.sample_feature')

    # * test: fallback_to_default_index
    def test_fallback_to_default_index(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test that a repository miss falls back to a matching default_feature_index entry.
        '''

        # Configure the service to miss so the fallback index is consulted.
        mock_dependencies['feature_service'].get.return_value = None

        # Execute with a default index containing the requested feature.
        result = test_ctx.handle(
            mock_dependencies,
            default_feature_index={'group.sample_feature': sample_feature},
        )

        # Assert the default feature is returned.
        assert result is sample_feature
        mock_dependencies['feature_service'].get.assert_called_once_with('group.sample_feature')

    # * test: miss_with_nonmatching_index
    def test_miss_with_nonmatching_index(self, test_ctx, mock_dependencies):
        '''
        Test that a repository miss with no matching default raises FEATURE_NOT_FOUND.
        '''

        # Configure the service to miss.
        mock_dependencies['feature_service'].get.return_value = None

        # Execute with a default index that does not contain the requested feature.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                default_feature_index={'other.feature': mock.Mock()},
            )

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.FEATURE_NOT_FOUND_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_list_features
@use_tester(
    type='domain_event',
    target_cls=ListFeatures,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(group_id=None),
    required_params=[],
)
class TestListFeatures:
    '''
    Tests for ListFeatures using the domain event test harness.
    '''

    # * test: all
    def test_all(self, test_ctx, sample_feature):
        '''
        Test listing all features.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return features.
        mock_dependencies['feature_service'].list.return_value = [sample_feature]

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert.
        assert result == [sample_feature]
        mock_dependencies['feature_service'].list.assert_called_once_with(group_id=None)

    # * test: by_group_id
    def test_by_group_id(self, test_ctx, sample_feature):
        '''
        Test listing features filtered by group_id.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return features.
        mock_dependencies['feature_service'].list.return_value = [sample_feature]

        # Execute with group_id override.
        result = test_ctx.handle(mock_dependencies, group_id='group')

        # Assert.
        assert result == [sample_feature]
        mock_dependencies['feature_service'].list.assert_called_once_with(group_id='group')

    # * test: empty_result
    def test_empty_result(self, test_ctx):
        '''
        Test listing features when the service returns an empty list.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return an empty list.
        mock_dependencies['feature_service'].list.return_value = []

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert.
        assert result == []
        mock_dependencies['feature_service'].list.assert_called_once_with(group_id=None)

# ** tester: test_remove_feature
@use_tester(
    type='domain_event',
    target_cls=RemoveFeature,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(id='group.sample_feature'),
    required_params=['id'],
)
class TestRemoveFeature:
    '''
    Tests for RemoveFeature using the domain event test harness.
    '''

    # * test: success
    def test_success(self, test_ctx):
        '''
        Test successful deletion of a feature.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the feature ID is returned.
        assert result == 'group.sample_feature'
        mock_dependencies['feature_service'].delete.assert_called_once_with('group.sample_feature')

    # * test: idempotent_multiple_calls
    def test_idempotent_multiple_calls(self, test_ctx):
        '''
        Test idempotent deletion with multiple calls.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Call twice.
        result_first = test_ctx.handle(mock_dependencies)
        result_second = test_ctx.handle(mock_dependencies)

        # Both should succeed.
        assert result_first == 'group.sample_feature'
        assert result_second == 'group.sample_feature'
        assert mock_dependencies['feature_service'].delete.call_count == 2

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** tester: test_update_feature
@use_tester(
    type='service_event',
    target_cls=UpdateFeature,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        id='group.sample_feature',
        attribute='name',
        value='Updated Feature Name',
    ),
    required_params=['id', 'attribute'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.feature',
        attribute='name',
        value='Updated Feature Name',
    ),
)
class TestUpdateFeature:
    '''
    Tests for UpdateFeature using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: name_success
    def test_name_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test successfully updating a feature name.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the name was updated.
        assert result is sample_feature
        assert result.name == 'Updated Feature Name'
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: description_success
    def test_description_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test successfully updating a feature description.
        '''

        # Execute with description override.
        result = test_ctx.handle(
            mock_dependencies,
            attribute='description',
            value='Updated description.',
        )

        # Assert the description was updated.
        assert result is sample_feature
        assert result.description == 'Updated description.'
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: clear_description
    def test_clear_description(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test clearing a feature description.
        '''

        # Execute with None value.
        result = test_ctx.handle(
            mock_dependencies,
            attribute='description',
            value=None,
        )

        # Assert the description was cleared.
        assert result is sample_feature
        assert result.description is None

    # * test: invalid_attribute
    def test_invalid_attribute(self, test_ctx, mock_dependencies):
        '''
        Test that an unsupported attribute raises INVALID_FEATURE_ATTRIBUTE.
        '''

        # Execute with invalid attribute.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, attribute='invalid', value='ignored')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.INVALID_FEATURE_ATTRIBUTE_ID
        mock_dependencies['feature_service'].get.assert_not_called()

    # * test: missing_name_value
    def test_missing_name_value(self, test_ctx, mock_dependencies):
        '''
        Test that updating name with empty value raises FEATURE_NAME_REQUIRED.
        '''

        # Execute with empty name value.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, attribute='name', value=' ')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.FEATURE_NAME_REQUIRED_ID
        mock_dependencies['feature_service'].get.assert_not_called()

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_add_feature_step
@use_tester(
    type='service_event',
    target_cls=AddFeatureStep,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        id='group.sample_feature',
        name='do_something',
        service_id='container.attribute',
        parameters={'foo': 'bar'},
        data_key='result_key',
        pass_on_error=True,
    ),
    required_params=['id', 'name', 'service_id'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.feature',
        name='do_something',
        service_id='container.attribute',
    ),
)
class TestAddFeatureStep:
    '''
    Tests for AddFeatureStep using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: append_success
    def test_append_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test successfully appending a new step to a feature.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the feature ID is returned.
        assert result == sample_feature.id

        # Assert a step was appended.
        assert len(sample_feature.steps) == 1
        step = sample_feature.steps[0]
        assert step.name == 'do_something'
        assert step.service_id == 'container.attribute'
        assert step.parameters == {'foo': 'bar'}
        assert step.data_key == 'result_key'
        assert step.pass_on_error is True

        # Verify service calls.
        mock_dependencies['feature_service'].get.assert_called_once_with(sample_feature.id)
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: insert_success
    def test_insert_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test inserting a step at a specific position.
        '''

        # Pre-populate the feature with two steps.
        sample_feature.add_step(
            name='first',
            service_id='container.first',
            parameters={'index': 0},
            data_key='first_key',
            pass_on_error=False,
        )
        sample_feature.add_step(
            name='second',
            service_id='container.second',
            parameters={'index': 1},
            data_key='second_key',
        )

        # Execute inserting at position 1.
        result = test_ctx.handle(
            mock_dependencies,
            name='inserted',
            service_id='container.inserted',
            parameters={'index': 1},
            data_key='inserted_key',
            position=1,
        )

        # Assert correct ordering.
        assert result == sample_feature.id
        assert len(sample_feature.steps) == 3
        assert sample_feature.steps[0].name == 'first'
        assert sample_feature.steps[1].name == 'inserted'
        assert sample_feature.steps[2].name == 'second'

        # Assert the inserted step has the correct service_id.
        inserted = sample_feature.steps[1]
        assert inserted.service_id == 'container.inserted'

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_update_feature_step
@use_tester(
    type='service_event',
    target_cls=UpdateFeatureStep,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        id='group.sample_feature',
        position=0,
        attribute='name',
        value='updated_name',
    ),
    required_params=['id', 'position', 'attribute'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.feature',
        position=0,
        attribute='name',
        value='Updated Name',
    ),
)
class TestUpdateFeatureStep:
    '''
    Tests for UpdateFeatureStep using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature with a step.
        '''

        # Pre-populate the feature with a single step.
        sample_feature.add_step(
            name='original',
            service_id='container.original',
            parameters={'foo': 'bar'},
            data_key='original_key',
            pass_on_error=False,
        )

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: update_string_attributes_success
    @pytest.mark.parametrize(
        'attribute, new_value, getter',
        [
            ('name', 'updated_name', lambda cmd: cmd.name),
            ('service_id', 'container.updated', lambda cmd: cmd.service_id),
            ('data_key', 'updated_key', lambda cmd: cmd.data_key),
        ],
    )
    def test_update_string_attributes_success(
            self,
            test_ctx,
            mock_dependencies,
            sample_feature,
            attribute,
            new_value,
            getter,
        ):
        '''
        Test successfully updating simple string attributes on a feature step.
        '''

        # Execute via the harness.
        step = sample_feature.steps[0]
        result = test_ctx.handle(
            mock_dependencies,
            attribute=attribute,
            value=new_value,
        )

        # Assert the update was applied.
        assert result == sample_feature.id
        assert getter(step) == new_value
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: update_parameters_success
    def test_update_parameters_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test updating the parameters attribute on a feature step.
        '''

        # Execute via the harness with parameters update.
        step = sample_feature.steps[0]
        result = test_ctx.handle(
            mock_dependencies,
            attribute='parameters',
            value={'baz': 'qux', 'foo': None},
        )

        # Assert the parameters were merged.
        assert result == sample_feature.id
        assert step.parameters == {'baz': 'qux'}

    # * test: update_pass_on_error_success
    def test_update_pass_on_error_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test updating the pass_on_error flag.
        '''

        # Execute via the harness.
        step = sample_feature.steps[0]
        result = test_ctx.handle(
            mock_dependencies,
            attribute='pass_on_error',
            value=True,
        )

        # Assert the flag was updated.
        assert result == sample_feature.id
        assert step.pass_on_error is True

    # * test: invalid_attribute
    def test_invalid_attribute(self, test_ctx, mock_dependencies):
        '''
        Test that an unsupported attribute raises INVALID_FEATURE_COMMAND_ATTRIBUTE.
        '''

        # Execute with invalid attribute.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, attribute='invalid')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.INVALID_FEATURE_COMMAND_ATTRIBUTE_ID
        mock_dependencies['feature_service'].get.assert_not_called()

    # * test: missing_name_or_service_id_value
    @pytest.mark.parametrize('attribute', ['name', 'service_id'])
    def test_missing_name_or_service_id_value(self, test_ctx, mock_dependencies, attribute):
        '''
        Test that updating name or service_id with empty value raises COMMAND_PARAMETER_REQUIRED.
        '''

        # Execute with empty value.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, attribute=attribute, value=' ')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.COMMAND_PARAMETER_REQUIRED_ID
        mock_dependencies['feature_service'].get.assert_not_called()

    # * test: step_not_found
    def test_step_not_found(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test that updating a step at an invalid position raises FEATURE_COMMAND_NOT_FOUND.
        '''

        # Execute with an out-of-range position.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, position=5)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.FEATURE_COMMAND_NOT_FOUND_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_remove_feature_step
@use_tester(
    type='service_event',
    target_cls=RemoveFeatureStep,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        id='group.sample_feature',
        position=0,
    ),
    required_params=['id', 'position'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.feature',
        position=0,
    ),
)
class TestRemoveFeatureStep:
    '''
    Tests for RemoveFeatureStep using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test successfully removing a step at a valid position.
        '''

        # Pre-populate the feature with two steps.
        first = sample_feature.add_step(
            name='first',
            service_id='container.first',
            parameters={'index': 0},
            data_key='first_key',
        )
        second = sample_feature.add_step(
            name='second',
            service_id='container.second',
            parameters={'index': 1},
            data_key='second_key',
        )

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the first step was removed.
        assert result == sample_feature.id
        assert sample_feature.steps == [second]
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: invalid_position_idempotent
    def test_invalid_position_idempotent(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test idempotent behavior when an invalid position is provided.
        '''

        # Pre-populate the feature with a single step.
        original = sample_feature.add_step(
            name='only',
            service_id='container.only',
            parameters={'index': 0},
            data_key='only_key',
        )

        # Execute with out-of-range position.
        result = test_ctx.handle(mock_dependencies, position=5)

        # Assert the steps list is unchanged.
        assert result == sample_feature.id
        assert sample_feature.steps == [original]
        mock_dependencies['feature_service'].save.assert_called_once_with(sample_feature)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: test_reorder_feature_step
@use_tester(
    type='service_event',
    target_cls=ReorderFeatureStep,
    dependencies={
        'feature_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'FeatureService',
        },
    },
    sample_kwargs=dict(
        id='group.sample_feature',
        start_position=0,
        end_position=2,
    ),
    required_params=['id', 'start_position', 'end_position'],
    service_attr='feature_service',
    not_found_error_code=a.error.FEATURE_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.feature',
        start_position=0,
        end_position=1,
    ),
)
class TestReorderFeatureStep:
    '''
    Tests for ReorderFeatureStep using the service event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, sample_feature) -> dict:
        '''
        Override to pre-configure get to return the sample feature.
        '''

        # Create the mock feature service.
        service = mock.Mock(spec=FeatureService)
        service.get.return_value = sample_feature
        return {'feature_service': service}

    # * test: forward
    def test_forward(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test moving a feature step forward in the workflow.
        '''

        # Populate.
        first, second, third = _populate_three_steps(sample_feature)

        # Execute: move first to end.
        result = test_ctx.handle(mock_dependencies, start_position=0, end_position=2)

        # Assert ordering.
        assert result == sample_feature.id
        assert sample_feature.steps == [second, third, first]

    # * test: backward
    def test_backward(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test moving a feature step backward in the workflow.
        '''

        # Populate.
        first, second, third = _populate_three_steps(sample_feature)

        # Execute: move last to front.
        result = test_ctx.handle(mock_dependencies, start_position=2, end_position=0)

        # Assert ordering.
        assert result == sample_feature.id
        assert sample_feature.steps == [third, first, second]

    # * test: clamp_low
    def test_clamp_low(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test that end_position is clamped to the start of the list when below 0.
        '''

        # Populate.
        first, second, third = _populate_three_steps(sample_feature)

        # Execute with negative end_position.
        result = test_ctx.handle(mock_dependencies, start_position=2, end_position=-5)

        # Assert clamped to front.
        assert result == sample_feature.id
        assert sample_feature.steps == [third, first, second]

    # * test: clamp_high
    def test_clamp_high(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test that end_position is clamped to the end of the list when above max.
        '''

        # Populate.
        first, second, third = _populate_three_steps(sample_feature)

        # Execute with large end_position.
        result = test_ctx.handle(mock_dependencies, start_position=0, end_position=10)

        # Assert clamped to end.
        assert result == sample_feature.id
        assert sample_feature.steps == [second, third, first]

    # * test: invalid_start_position_idempotent
    def test_invalid_start_position_idempotent(self, test_ctx, mock_dependencies, sample_feature):
        '''
        Test idempotent behavior when start_position is out of range.
        '''

        # Populate with two steps.
        first = sample_feature.add_step(
            name='first',
            service_id='container.first',
            parameters={'index': 0},
            data_key='first_key',
        )
        second = sample_feature.add_step(
            name='second',
            service_id='container.second',
            parameters={'index': 1},
            data_key='second_key',
        )
        original_steps = list(sample_feature.steps)

        # Execute with out-of-range start.
        result = test_ctx.handle(mock_dependencies, start_position=5, end_position=0)

        # Assert unchanged.
        assert result == sample_feature.id
        assert sample_feature.steps == original_steps

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

