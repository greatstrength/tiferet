"""Tiferet Utils Check Tests"""

# *** imports

# ** core
import inspect
from types import SimpleNamespace
from unittest import mock

# ** infra
import pytest

# ** app
from tiferet.events.tester_phase import EvaluateAssertion
from tiferet.interfaces import CheckService
from tiferet.utils.tester_check import Check

# *** fixtures

# ** fixture: check
@pytest.fixture
def check() -> Check:
    '''
    Provide a check.

    :return: The check.
    :rtype: Check
    '''

    # The check holds no state.
    return Check()

# *** tests

# ** test: none_never_matches_a_mapping
@pytest.mark.parametrize('exact', [False, True])
def test_none_never_matches_a_mapping(check: Check, exact: bool) -> None:
    '''A None actual fails an empty or non-empty expected mapping, at any depth.'''

    # Top level, empty and non-empty, under fields and equals.
    assert check.equal(None, {}, exact=exact) == 'Expected a mapping, found None.'
    assert check.equal(None, {'a': 1}, exact=exact) == 'Expected a mapping, found None.'

    # Nested.
    assert check.equal({'parameters': None}, {'parameters': {}}, exact=exact) == 'Expected a mapping, found None.'

# ** test: empty_mapping_matches_only_an_empty_mapping
@pytest.mark.parametrize('exact', [False, True])
def test_empty_mapping_matches_only_an_empty_mapping(check: Check, exact: bool) -> None:
    '''An expected {} matches only a mapping with no keys.'''

    # Nested extra key, nested empty, and a non-mapping object.
    assert check.equal(
        {'parameters': {'config_file': 'x'}},
        {'parameters': {}},
        exact=exact,
    ) == 'Expected an empty mapping, found key config_file.'
    assert check.equal({'parameters': {}}, {'parameters': {}}, exact=exact) is None
    assert check.equal({}, {}, exact=exact) is None
    assert check.equal(SimpleNamespace(), {}, exact=exact) == 'Expected an empty mapping, found SimpleNamespace.'

# ** test: equals_rejects_extra_keys
def test_equals_rejects_extra_keys(check: Check) -> None:
    '''Exact rejects an extra mapping key and names it. The default ignores it.'''

    # Top level.
    assert check.equal({'a': 1, 'b': 2}, {'a': 1}, exact=True) == 'Unexpected key b.'
    assert check.equal({'a': 1}, {'a': 1}, exact=True) is None
    assert check.equal({'a': 1, 'b': 2}, {'a': 1}) is None

    # Nested inside a list and inside an object attribute.
    assert check.equal([{'a': 1, 'b': 2}], [{'a': 1}], exact=True) == 'Unexpected key b.'
    holder = SimpleNamespace(inner={'a': 1, 'c': 3})
    assert check.equal(holder, {'inner': {'a': 1}}, exact=True) == 'Unexpected key c.'
    assert check.equal(holder, {'inner': {'a': 1}}) is None

# ** test: equals_object_keeps_attribute_compare
def test_equals_object_keeps_attribute_compare(check: Check) -> None:
    '''An object actual under exact still compares only the named attributes.'''

    # Extra attributes on an object are not listed.
    obj = SimpleNamespace(a=1, b=2)
    assert check.equal(obj, {'a': 1}, exact=True) is None
    assert check.equal(obj, {'a': 2}, exact=True) == '1 != 2.'
    assert check.equal(obj, {'c': 1}, exact=True) == 'Missing attribute c.'

# ** test: keyed_list_unchanged
def test_keyed_list_unchanged(check: Check) -> None:
    '''The keyed-list form still ignores extra keys inside a matched item.'''

    # Items are compared as fields, even under exact.
    actual = [SimpleNamespace(id='x', data={'a': 1, 'b': 2})]
    expected = {'key': 'id', 'items': {'x': {'data': {'a': 1}}}}
    assert check.equal(actual, expected, exact=True) is None
    assert check.equal(actual, expected) is None

# ** test: equal_exact_keyword
def test_equal_exact_keyword() -> None:
    '''CheckService.equal and Check.equal take exact with a False default.'''

    # Both signatures carry the keyword.
    for target in (CheckService.equal, Check.equal):
        parameter = inspect.signature(target).parameters['exact']
        assert parameter.default is False

# ** test: only_equals_passes_exact
@pytest.mark.parametrize('name, exact', [('equals', True), ('fields', False)])
def test_only_equals_passes_exact(name: str, exact: bool) -> None:
    '''The equals branch passes exact=True. The fields branch keeps the default.'''

    # A mock service records the call.
    service = mock.Mock(spec=CheckService)
    service.equal.return_value = None
    event = EvaluateAssertion(check_service=service)
    event.execute(
        assertion=SimpleNamespace(check=name),
        values={'outcome': {'a': 1}, name: {'a': 1}},
    )
    args, kwargs = service.equal.call_args
    assert args == ({'a': 1}, {'a': 1})
    assert kwargs.get('exact', False) is exact
