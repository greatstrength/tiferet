"""Tiferet Utils Check"""

# *** imports

# ** core
from collections.abc import Mapping
from typing import Any, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..interfaces.check import CheckService
from ..interfaces.core import ServiceError
from ..mappers.core import Aggregate, TransferObject

# *** constants

# ** constant: check_call_invalid
CHECK_CALL_INVALID = 'CHECK_CALL_INVALID'

# *** functions

# ** function: reject_call
def _reject_call(service: Any, message: str) -> None:
    '''
    Raise the uncatalogued bad-call code.

    The code sits beside ``ServiceError.raise_for``. It is not a catalogued
    ``a.error`` code and it has no language entry.

    :param service: The check instance that rejected the call.
    :type service: Any
    :param message: The defect message.
    :type message: str
    :return: None.
    :rtype: None
    '''

    # A bad call is infrastructural. It is not a recorded check failure.
    ServiceError.raise_for(
        service,
        CHECK_CALL_INVALID,
        message=message,
    )

# *** utils

# ** util: check
class Check(CheckService):
    '''
    Compares values during one check and returns a mismatch or ``None``.

    It does not see the module, the node id, or the failure pool, and it does
    not read or write the test-module document.
    '''

    # * method: equal
    def equal(self, actual: Any, expected: Any) -> str | None:
        '''
        Compare two values, including a structural compare.

        :param actual: The value under check.
        :type actual: Any
        :param expected: The expected value.
        :type expected: Any
        :return: A mismatch, or None when the values match.
        :rtype: str | None
        '''

        # A keyed list replaces field index paths. It is not an index path.
        if (
            isinstance(expected, dict)
            and isinstance(actual, list)
            and self._is_keyed_list(expected)
        ):
            return self._equal_keyed(actual, expected)
        if isinstance(expected, dict):
            return self._equal_mapping(actual, expected)
        if isinstance(expected, list):
            if not isinstance(actual, list) or len(actual) != len(expected):
                return 'List field length does not match.'
            for actual_item, expected_item in zip(actual, expected):
                mismatch = self.equal(actual_item, expected_item)
                if mismatch:
                    return mismatch
            return None
        if actual != expected:
            return f'{actual!r} != {expected!r}.'
        return None

    # * method: codes
    def codes(self, actual: str, expected: str) -> str | None:
        '''
        Compare two error-code strings.

        :param actual: The code that was read.
        :type actual: str
        :param expected: The code that was required.
        :type expected: str
        :return: A mismatch, or None when the codes match.
        :rtype: str | None
        '''

        # A non-string is a bad call, not a mismatch and not a model import.
        if not isinstance(actual, str) or not isinstance(expected, str):
            _reject_call(self, 'codes compares two error-code strings.')
        if actual != expected:
            return f'{actual!r} != {expected!r}.'
        return None

    # * method: role_dump
    def role_dump(self, dumped: Any, exclude: Any) -> str | None:
        '''
        Compare a dump to an exclude set.

        :param dumped: The dumped mapping.
        :type dumped: Any
        :param exclude: Names that must be absent from the dump.
        :type exclude: Any
        :return: A mismatch, or None when every excluded name is absent.
        :rtype: str | None
        '''

        # A dump that is not a mapping is a bad call.
        if not isinstance(dumped, Mapping):
            _reject_call(self, 'role_dump requires a mapping.')
        if exclude is None:
            exclude = []
        if isinstance(exclude, (str, bytes)) or not isinstance(exclude, (list, set, tuple)):
            _reject_call(self, 'role_dump exclude is a set of names.')

        # An excluded name that is present is the mismatch.
        for name in set(exclude):
            if name in dumped:
                return f'{name} is in the dump.'
        return None

    # * method: mapper_contract
    def mapper_contract(self, exclude: Any, source: Any) -> str | None:
        '''
        Run the mapper protocol and return one mismatch or None.

        The harness owns the aggregate and transfer-object bases. ``source``
        is already built. This method does not construct a domain object.

        :param exclude: Names the to_data role excludes. Compared as a set.
        :type exclude: Any
        :param source: The domain source ``from_model`` copies.
        :type source: Any
        :return: A mismatch, or None when the protocol holds.
        :rtype: str | None
        '''

        # A missing source or a non-list exclude is a bad call.
        if source is None or not hasattr(source, 'model_dump'):
            _reject_call(self, 'mapper_contract requires a source.')
        if exclude is not None and not isinstance(exclude, list):
            _reject_call(self, 'mapper_contract exclude is a list.')
        excluded = set(exclude or [])

        # The harness owns the aggregate base.
        class TestAggregate(Aggregate):
            '''Harness aggregate for the mapper contract.'''

            id: str = Field(
                ...,
                description='The identifier.',
            )

            name: str = Field(
                ...,
                description='The name.',
            )

        # The harness owns the transfer-object base.
        class TestDataObject(TransferObject):
            '''Harness transfer object for the mapper contract.'''

            _ROLES = {
                'to_data': {
                    'exclude': excluded,
                },
                'to_model': {},
            }

            id: str = Field(
                ...,
                description='The identifier.',
            )

            name: str = Field(
                ...,
                description='The name.',
            )

        # Construction.
        aggregate = TestAggregate(id='test_id', name='Test Aggregate')
        mismatch = self.equal(aggregate.id, 'test_id')
        if mismatch:
            return mismatch
        mismatch = self.equal(aggregate.name, 'Test Aggregate')
        if mismatch:
            return mismatch

        # set_attribute writes a known field.
        aggregate.set_attribute('name', 'Updated Name')
        mismatch = self.equal(aggregate.name, 'Updated Name')
        if mismatch:
            return mismatch

        # An unknown attribute is INVALID_MODEL_ATTRIBUTE.
        mismatch = self._expect_code(
            lambda: aggregate.set_attribute('invalid_attribute', 'value'),
            'INVALID_MODEL_ATTRIBUTE',
            'Unknown attribute should fail.',
        )
        if mismatch:
            return mismatch

        # An invalid value is INVALID_MODEL_VALUE.
        mismatch = self._expect_code(
            lambda: aggregate.set_attribute('name', ['not', 'a', 'string']),
            'INVALID_MODEL_VALUE',
            'Invalid value should fail.',
        )
        if mismatch:
            return mismatch

        # model_validate builds the transfer object from data.
        validated = TestDataObject.model_validate({
            'id': 'test_id',
            'name': 'Test Data',
        })
        if not isinstance(validated, TestDataObject):
            return 'model_validate did not build the transfer object.'
        mismatch = self.equal(validated.name, 'Test Data')
        if mismatch:
            return mismatch

        # from_model copies the source the event already built.
        copied = TestDataObject.from_model(source)
        if not isinstance(copied, TestDataObject):
            return 'from_model did not copy the source.'
        mismatch = self.equal(copied.id, 'test_id')
        if mismatch:
            return mismatch
        mismatch = self.equal(copied.name, 'Test Model')
        if mismatch:
            return mismatch

        # map returns the aggregate class.
        mapped = copied.map(TestAggregate)
        if not isinstance(mapped, TestAggregate):
            return 'map did not return the aggregate class.'
        mismatch = self.equal(mapped.id, 'test_id')
        if mismatch:
            return mismatch

        # The exclude list is a set, not a YAML set.
        if set(TestDataObject._ROLES['to_data']['exclude']) != excluded:
            return 'The exclude list was not compared as a set.'
        data_object = TestDataObject(id='test_id', name='Test Data')

        # to_data omits the excluded names.
        to_data = data_object.to_primitive(role='to_data')
        mismatch = self.role_dump(to_data, excluded)
        if mismatch:
            return mismatch
        if 'id' not in excluded:
            mismatch = self.equal(to_data.get('id'), 'test_id')
            if mismatch:
                return mismatch
        if 'name' not in excluded:
            mismatch = self.equal(to_data.get('name'), 'Test Data')
            if mismatch:
                return mismatch

        # to_model includes the fields.
        to_model = data_object.to_primitive(role='to_model')
        mismatch = self.equal(to_model.get('id'), 'test_id')
        if mismatch:
            return mismatch
        mismatch = self.equal(to_model.get('name'), 'Test Data')
        if mismatch:
            return mismatch

        # An unknown role falls back to the default dump.
        fallback = data_object.to_primitive(role='unknown_role')
        mismatch = self.equal(fallback.get('id'), 'test_id')
        if mismatch:
            return mismatch
        return self.equal(fallback.get('name'), 'Test Data')

    # * method: is_keyed_list
    def _is_keyed_list(self, expected: Dict[str, Any]) -> bool:
        '''
        Report whether an expected value is the keyed-list form.

        :param expected: The expected mapping.
        :type expected: Dict[str, Any]
        :return: True when the mapping is key plus items.
        :rtype: bool
        '''

        # The form is exactly those two keys. Other mappings are attributes.
        return (
            set(expected) == {'key', 'items'}
            and isinstance(expected.get('key'), str)
            and isinstance(expected.get('items'), dict)
        )

    # * method: equal_mapping
    def _equal_mapping(self, actual: Any, expected: Dict[str, Any]) -> str | None:
        '''
        Compare a mapping or an object's attributes. A missing expected key fails.

        :param actual: The actual mapping or object.
        :type actual: Any
        :param expected: The expected attributes.
        :type expected: Dict[str, Any]
        :return: A mismatch, or None when the named keys match.
        :rtype: str | None
        '''

        # A mapping compares keys. An object compares attributes.
        if isinstance(actual, Mapping):
            for key, item in expected.items():
                if key not in actual:
                    return f'Missing key {key}.'
                mismatch = self.equal(actual[key], item)
                if mismatch:
                    return mismatch
            return None
        for key, item in expected.items():
            if not hasattr(actual, key):
                return f'Missing attribute {key}.'
            mismatch = self.equal(getattr(actual, key), item)
            if mismatch:
                return mismatch
        return None

    # * method: equal_keyed
    def _equal_keyed(self, actual: List[Any], expected: Dict[str, Any]) -> str | None:
        '''
        Match a list of objects to a mapping keyed by one attribute.

        :param actual: The actual list.
        :type actual: List[Any]
        :param expected: The keyed-list form.
        :type expected: Dict[str, Any]
        :return: A mismatch, or None when the keyed items match.
        :rtype: str | None
        '''

        # Every object matches one item, and every item matches one object.
        attr = expected['key']
        items = expected['items']
        if len(actual) != len(items):
            return 'Keyed list length does not match items.'
        seen = {}
        for obj in actual:
            if not hasattr(obj, attr):
                return f'Missing key attribute {attr}.'
            key = getattr(obj, attr)
            if key in seen:
                return f'Duplicate key {key}.'
            seen[key] = obj
        if set(seen) != set(items):
            return 'Keyed list keys do not match items.'
        for key, fields in items.items():
            mismatch = self.equal(seen[key], fields)
            if mismatch:
                return mismatch
        return None

    # * method: expect_code
    def _expect_code(self, call: Any, expected: str, absent: str) -> str | None:
        '''
        Compare the error code a call raises. The code is a string.

        :param call: The call that should raise.
        :type call: Any
        :param expected: The expected error-code string.
        :type expected: str
        :param absent: The mismatch when the call does not raise.
        :type absent: str
        :return: A mismatch, or None when the code matches.
        :rtype: str | None
        '''

        # Read the code off the exception. Do not import a model error.
        try:
            call()
        except Exception as error:
            code = getattr(error, 'error_code', None)
            if not isinstance(code, str):
                return absent
            return self.codes(code, expected)
        return absent
