"""Tiferet Utils Check"""

# *** imports

# ** core
from collections.abc import Mapping
from typing import Any, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..interfaces.tester_check import CheckService
from ..interfaces.core import ServiceError
from ..mappers.core import Aggregate, TransferObject

# *** constants

# ** constant: check_call_invalid
CHECK_CALL_INVALID = 'CHECK_CALL_INVALID'

# *** utils

# ** util: check
class Check(CheckService):
    '''
    Compares values during one check and returns a mismatch or ``None``.

    It does not see the module, the node id, or the failure pool, and it does
    not read or write the test-module document.
    '''

    # * method: reject_call
    def _reject_call(self, message: str) -> None:
        '''
        Raise the uncatalogued bad-call code.

        The code is not a catalogued phase error and has no language entry.

        :param message: Defect text passed as the message keyword.
        :type message: str
        '''

        # Raise the local uncatalogued bad-call code.
        ServiceError.raise_for(self, CHECK_CALL_INVALID, message=message)

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

        # Dispatch keyed-list form when expected is keyed and actual is a list.
        if isinstance(expected, dict) and isinstance(actual, list) and self._is_keyed_list(expected):
            return self._equal_keyed(actual, expected)

        # Compare a mapping of expected attributes or keys.
        if isinstance(expected, dict):
            return self._equal_mapping(actual, expected)

        # Compare lists pairwise when expected is a list.
        if isinstance(expected, list):
            if not isinstance(actual, list) or len(actual) != len(expected):
                return 'List field length does not match.'

            # Return the first pairwise mismatch.
            for actual_item, expected_item in zip(actual, expected):
                mismatch = self.equal(actual_item, expected_item)
                if mismatch is not None:
                    return mismatch

            return None

        # Scalar compare with stable mismatch text.
        if actual != expected:
            return f'{actual!r} != {expected!r}.'

        # Values match.
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

        # Reject non-string codes as a bad call.
        if not isinstance(actual, str) or not isinstance(expected, str):
            self._reject_call('codes compares two error-code strings.')

        # Return the scalar mismatch text when the codes differ.
        if actual != expected:
            return f'{actual!r} != {expected!r}.'

        # Codes match.
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

        # Reject a non-mapping dump as a bad call.
        if not isinstance(dumped, Mapping):
            self._reject_call('role_dump requires a mapping.')

        # Treat a null exclude as an empty list.
        if exclude is None:
            exclude = []

        # Reject a string, bytes, or non-collection exclude as a bad call.
        if isinstance(exclude, (str, bytes)) or not isinstance(exclude, (list, set, tuple)):
            self._reject_call('role_dump exclude is a set of names.')

        # Return the first excluded name still present in the dump.
        for name in set(exclude):
            if name in dumped:
                return f'{name} is in the dump.'

        # Every excluded name is absent.
        return None

    # * method: mapper_contract
    def mapper_contract(self, exclude: Any, source: Any) -> str | None:
        '''
        Run the mapper protocol and return one mismatch or None.

        The caller supplies ``source``. This method builds the aggregate and
        transfer-object bases and does not construct the domain source.

        :param exclude: Names the to_data role excludes. Compared as a set.
        :type exclude: Any
        :param source: The domain source from_model copies. Already built.
        :type source: Any
        :return: A mismatch, or None when the protocol holds.
        :rtype: str | None
        '''

        # Reject a missing source that cannot dump.
        if source is None or not hasattr(source, 'model_dump'):
            self._reject_call('mapper_contract requires a source.')

        # Reject a non-list exclude when one is supplied.
        if exclude is not None and not isinstance(exclude, list):
            self._reject_call('mapper_contract exclude is a list.')

        # Compare excluded names as a set; null means no names.
        excluded = set(exclude or [])

        # Build local aggregate and transfer-object bases for the protocol.
        class TestAggregate(Aggregate):
            id: str = Field(..., description='The identifier.')
            name: str = Field(..., description='The name.')

        class TestDataObject(TransferObject):
            id: str = Field(..., description='The identifier.')
            name: str = Field(..., description='The name.')
            _ROLES = {
                'to_data': {
                    'exclude': excluded,
                },
                'to_model': {
                },
            }

        # Construct the sample aggregate and compare identity fields.
        aggregate = TestAggregate(id='test_id', name='Test Aggregate')
        mismatch = self.equal(aggregate.id, 'test_id')
        if mismatch is not None:
            return mismatch
        mismatch = self.equal(aggregate.name, 'Test Aggregate')
        if mismatch is not None:
            return mismatch

        # Mutate a valid attribute and compare the result.
        aggregate.set_attribute('name', 'Updated Name')
        mismatch = self.equal(aggregate.name, 'Updated Name')
        if mismatch is not None:
            return mismatch

        # An unknown attribute must raise INVALID_MODEL_ATTRIBUTE.
        mismatch = self._expect_code(
            lambda: aggregate.set_attribute('invalid_attribute', 'value'),
            'INVALID_MODEL_ATTRIBUTE',
            'Unknown attribute should fail.',
        )
        if mismatch is not None:
            return mismatch

        # An invalid value must raise INVALID_MODEL_VALUE.
        mismatch = self._expect_code(
            lambda: aggregate.set_attribute('name', ['not', 'a', 'string']),
            'INVALID_MODEL_VALUE',
            'Invalid value should fail.',
        )
        if mismatch is not None:
            return mismatch

        # model_validate must build the transfer object.
        validated = TestDataObject.model_validate({
            'id': 'test_id',
            'name': 'Test Data',
        })
        if not isinstance(validated, TestDataObject):
            return 'model_validate did not build the transfer object.'
        mismatch = self.equal(validated.name, 'Test Data')
        if mismatch is not None:
            return mismatch

        # from_model must copy the caller-supplied source.
        copied = TestDataObject.from_model(source)
        if not isinstance(copied, TestDataObject):
            return 'from_model did not copy the source.'
        mismatch = self.equal(copied.id, 'test_id')
        if mismatch is not None:
            return mismatch
        mismatch = self.equal(copied.name, 'Test Model')
        if mismatch is not None:
            return mismatch

        # map must return the aggregate class.
        mapped = copied.map(TestAggregate)
        if not isinstance(mapped, TestAggregate):
            return 'map did not return the aggregate class.'
        mismatch = self.equal(mapped.id, 'test_id')
        if mismatch is not None:
            return mismatch

        # The to_data exclude list must be compared as a set.
        if set(TestDataObject._ROLES['to_data']['exclude']) != excluded:
            return 'The exclude list was not compared as a set.'

        # to_data dump must omit excluded names and keep the rest.
        data_object = TestDataObject(id='test_id', name='Test Data')
        dumped = data_object.to_primitive(role='to_data')
        mismatch = self.role_dump(dumped, excluded)
        if mismatch is not None:
            return mismatch
        if 'id' not in excluded:
            mismatch = self.equal(dumped.get('id'), 'test_id')
            if mismatch is not None:
                return mismatch
        if 'name' not in excluded:
            mismatch = self.equal(dumped.get('name'), 'Test Data')
            if mismatch is not None:
                return mismatch

        # to_model dump must include both identity fields.
        dumped_model = data_object.to_primitive(role='to_model')
        mismatch = self.equal(dumped_model.get('id'), 'test_id')
        if mismatch is not None:
            return mismatch
        mismatch = self.equal(dumped_model.get('name'), 'Test Data')
        if mismatch is not None:
            return mismatch

        # An unknown role falls back to the default dump.
        dumped_unknown = data_object.to_primitive(role='unknown_role')
        mismatch = self.equal(dumped_unknown.get('id'), 'test_id')
        if mismatch is not None:
            return mismatch
        return self.equal(dumped_unknown.get('name'), 'Test Data')

    # * method: is_keyed_list
    def _is_keyed_list(self, expected: Dict[str, Any]) -> bool:
        '''
        Report whether an expected value is the keyed-list form.

        :param expected: The expected mapping.
        :type expected: Dict[str, Any]
        :return: True only for the keyed-list form.
        :rtype: bool
        '''

        # Require exactly key and items with the keyed-list shapes.
        return (
            set(expected.keys()) == {'key', 'items'}
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

        # Compare keys when actual is a mapping.
        if isinstance(actual, Mapping):
            for key, expected_value in expected.items():
                if key not in actual:
                    return f'Missing key {key}.'

                # Compare the present value.
                mismatch = self.equal(actual[key], expected_value)
                if mismatch is not None:
                    return mismatch

            return None

        # Compare attributes on a non-mapping object.
        for key, expected_value in expected.items():
            if not hasattr(actual, key):
                return f'Missing attribute {key}.'

            # Compare the present attribute value.
            mismatch = self.equal(getattr(actual, key), expected_value)
            if mismatch is not None:
                return mismatch

        return None

    # * method: equal_keyed
    def _equal_keyed(self, actual: List[Any], expected: Dict[str, Any]) -> str | None:
        '''
        Match a list of objects to a mapping keyed by one attribute.

        :param actual: The actual list.
        :type actual: List[Any]
        :param expected: The keyed-list form, with key and items.
        :type expected: Dict[str, Any]
        :return: A mismatch, or None when the keyed items match.
        :rtype: str | None
        '''

        # Compare list length to the items mapping size.
        items = expected['items']
        key_attr = expected['key']
        if len(actual) != len(items):
            return 'Keyed list length does not match items.'

        # Index objects by the named key attribute.
        seen: Dict[Any, Any] = {}
        for obj in actual:
            if not hasattr(obj, key_attr):
                return f'Missing key attribute {key_attr}.'

            # Reject a duplicate key.
            key = getattr(obj, key_attr)
            if key in seen:
                return f'Duplicate key {key}.'
            seen[key] = obj

        # Require the seen keys to match the items keys.
        if set(seen.keys()) != set(items.keys()):
            return 'Keyed list keys do not match items.'

        # Compare each object to its item fields.
        for key, obj in seen.items():
            mismatch = self.equal(obj, items[key])
            if mismatch is not None:
                return mismatch

        return None

    # * method: expect_code
    def _expect_code(self, call: Any, expected: str, absent: str) -> str | None:
        '''
        Compare the error code a call raises. The code is a string.

        The code is read off the exception. The method does not import a model
        error.

        :param call: Callable that should raise.
        :type call: Any
        :param expected: The expected error-code string.
        :type expected: str
        :param absent: Mismatch when the call does not raise, or when error_code is not a string.
        :type absent: str
        :return: A mismatch, or None when the code matches.
        :rtype: str | None
        '''

        # Invoke the call and compare a raised error_code.
        try:
            call()
        except Exception as error:
            code = getattr(error, 'error_code', None)
            if not isinstance(code, str):
                return absent
            return self.codes(code, expected)

        # The call did not raise.
        return absent
