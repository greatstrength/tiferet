"""Tests for Tiferet Domain Test"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.test import TestContext
from tiferet.domain.feature import Feature
from tiferet.domain.test import Test

# *** constants

# ** constant: test_sample_data
TEST_SAMPLE_DATA = {
    'id': 'error.format',
    'name': 'Error Format',
    'conditions': {
        'fixtures': ['error_message'],
    },
    'execute': [
        {
            'target': 'error_message',
            'method': 'format',
            'as': 'raw',
        },
    ],
    'assert': [
        {
            'outcome': 'raw',
            'equals': 'An error occurred.',
        },
    ],
}

# *** testers

# ** tester: test_test
@use_tester(
    type='domain',
    target_cls=Test,
    sample_data=TEST_SAMPLE_DATA,
    expected_data={
        'id': 'error.format',
        'name': 'Error Format',
        'group_id': 'error',
        'feature_key': 'format',
    },
    equality_fields=['id', 'name', 'group_id', 'feature_key'],
)
class TestTest:
    '''Tests for Test construction, the three phase fields, and the registry.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Test derives its feature keys and keeps the three phases.'''

        test_ctx.assert_new()

    # * test: phases
    def test_phases(self, test_ctx) -> None:
        '''Verify the three phase fields, in order, and no fourth phase.'''

        # Construct the test from the declared sample.
        test = test_ctx.make_target()

        # A test is a feature, spoken as three phases.
        assert isinstance(test, Feature)
        assert list(Test.__dict__['__annotations__']) == [
            'conditions',
            'execute',
            'assert_',
        ]
        assert test.conditions == {'fixtures': ['error_message']}
        assert test.execute[0]['as'] == 'raw'
        assert test.assert_[0]['equals'] == 'An error occurred.'

        # There is no fourth phase field.
        assert 'variables' not in Test.model_fields

    # * test: assert_alias
    def test_assert_alias(self, test_ctx) -> None:
        '''Verify the assert phase loads and dumps under the name assert.'''

        # Construct from the YAML name, then dump back under that name.
        test = test_ctx.make_target()
        dumped = test.model_dump(by_alias=True)

        # The dialect name round-trips; the Python attribute does not leak.
        assert dumped['assert'] == test.assert_
        assert 'assert_' not in dumped

    # * test: registry
    def test_registry(self) -> None:
        '''Verify Feature stays on FeatureContext and Test maps to TestContext.'''

        # Feature is unchanged; Test is the extension point.
        assert BaseContext.for_domain(Feature) is FeatureContext
        assert BaseContext.for_domain(Test) is TestContext
        assert 'domain_type' in TestContext.__dict__
        assert TestContext.domain_type is Test
