"""Tiferet Utils Check Tests"""

# *** imports

# ** infra
import pytest
from pydantic import Field

# ** app
from tiferet import use_tester
from tiferet.domain.core import DomainObject
from tiferet.interfaces.core import ServiceError
from tiferet.utils.tester_check import Check

# *** fixtures

# ** fixture: contract_source
@pytest.fixture
def contract_source():
    '''
    Build a domain source with id test_id and name Test Model.

    :return: A ContractSource domain object.
    :rtype: DomainObject
    '''

    # Construct the domain source used by mapper_contract holds.
    class ContractSource(DomainObject):
        id: str = Field(...)
        name: str = Field(...)

    return ContractSource(id='test_id', name='Test Model')

# ** fixture: contract_source_other
@pytest.fixture
def contract_source_other():
    '''
    Build a domain source with id test_id and name Other Name.

    :return: A ContractSource domain object.
    :rtype: DomainObject
    '''

    # Construct the domain source used by mapper_contract mismatch.
    class ContractSource(DomainObject):
        id: str = Field(...)
        name: str = Field(...)

    return ContractSource(id='test_id', name='Other Name')

# *** testers

# ** tester: test_check
@use_tester(
    type='generic',
    target_cls=Check,
)
class TestCheck:
    '''
    Tests for the Check utility.
    '''

    # * fixture: check
    @pytest.fixture
    def check(self, test_ctx):
        '''
        Construct the Check target under test.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :return: A constructed Check instance.
        :rtype: Check
        '''

        # Build the Check target with empty sample data.
        return test_ctx.make_target()

    # * test: equal_match
    def test_equal_match(self, check):
        '''
        equal returns null when actual and expected match.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare matching scalars.
        assert check.equal(1, 1) is None

    # * test: equal_mismatch
    def test_equal_mismatch(self, check):
        '''
        equal returns the scalar mismatch text when values differ.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare differing scalars.
        assert check.equal(1, 2) == '1 != 2.'

    # * test: codes_match
    def test_codes_match(self, check):
        '''
        codes returns null when the error-code strings match.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare matching phase-code sample strings.
        assert check.codes('PHASE_STEP_FAILED', 'PHASE_STEP_FAILED') is None

    # * test: codes_mismatch
    def test_codes_mismatch(self, check):
        '''
        codes returns the scalar mismatch text when codes differ.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare differing phase-code sample strings.
        assert check.codes('PHASE_STEP_FAILED', 'PHASE_CHECK_FAILED') == (
            "'PHASE_STEP_FAILED' != 'PHASE_CHECK_FAILED'."
        )

    # * test: codes_bad_call
    def test_codes_bad_call(self, check):
        '''
        codes raises CHECK_CALL_INVALID when a code is not a string.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Call codes with a non-string actual.
        with pytest.raises(ServiceError) as exc_info:
            check.codes(1, 'PHASE_CHECK_FAILED')
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == 'codes compares two error-code strings.'

    # * test: role_dump_absent
    def test_role_dump_absent(self, check):
        '''
        role_dump returns null when every excluded name is absent.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Exclude a name that is not in the dump.
        assert check.role_dump({'id': 'a'}, ['name']) is None

    # * test: role_dump_present
    def test_role_dump_present(self, check):
        '''
        role_dump returns when an excluded name is present.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Exclude a name that is in the dump.
        assert check.role_dump({'id': 'a'}, ['id']) == 'id is in the dump.'

    # * test: role_dump_bad_dump
    def test_role_dump_bad_dump(self, check):
        '''
        role_dump raises when dumped is not a mapping.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Call role_dump with a list dump.
        with pytest.raises(ServiceError) as exc_info:
            check.role_dump([], [])
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == 'role_dump requires a mapping.'

    # * test: role_dump_bad_exclude
    def test_role_dump_bad_exclude(self, check):
        '''
        role_dump raises when exclude is a string.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Call role_dump with a string exclude.
        with pytest.raises(ServiceError) as exc_info:
            check.role_dump({'id': 'a'}, 'id')
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == 'role_dump exclude is a set of names.'

    # * test: mapper_contract_holds
    def test_mapper_contract_holds(self, check, contract_source):
        '''
        mapper_contract returns null when the protocol holds.

        :param check: The constructed Check.
        :type check: Check
        :param contract_source: Domain source with name Test Model.
        :type contract_source: DomainObject
        '''

        # Run the mapper protocol against a matching source.
        assert check.mapper_contract([], contract_source) is None

    # * test: mapper_contract_mismatch
    def test_mapper_contract_mismatch(self, check, contract_source_other):
        '''
        mapper_contract returns when the source name does not match.

        :param check: The constructed Check.
        :type check: Check
        :param contract_source_other: Domain source with name Other Name.
        :type contract_source_other: DomainObject
        '''

        # Run the mapper protocol against a mismatched source.
        assert check.mapper_contract([], contract_source_other) == (
            "'Other Name' != 'Test Model'."
        )

    # * test: mapper_contract_bad_source
    def test_mapper_contract_bad_source(self, check):
        '''
        mapper_contract raises when source is null.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Call mapper_contract with a null source.
        with pytest.raises(ServiceError) as exc_info:
            check.mapper_contract([], None)
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == 'mapper_contract requires a source.'

    # * test: mapper_contract_bad_exclude
    def test_mapper_contract_bad_exclude(self, check, contract_source):
        '''
        mapper_contract raises when exclude is a set.

        :param check: The constructed Check.
        :type check: Check
        :param contract_source: Domain source with name Test Model.
        :type contract_source: DomainObject
        '''

        # Call mapper_contract with a set exclude.
        with pytest.raises(ServiceError) as exc_info:
            check.mapper_contract({'id'}, contract_source)
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == 'mapper_contract exclude is a list.'

    # * test: is_keyed_list_holds
    def test_is_keyed_list_holds(self, check):
        '''
        _is_keyed_list returns True for the keyed-list form.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Report the keyed-list form.
        assert check._is_keyed_list({
            'key': 'id',
            'items': {},
        }) is True

    # * test: is_keyed_list_rejects
    def test_is_keyed_list_rejects(self, check):
        '''
        _is_keyed_list returns False for a non-keyed mapping.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Reject a plain attribute mapping.
        assert check._is_keyed_list({'id': 'a'}) is False

    # * test: equal_mapping_match
    def test_equal_mapping_match(self, check):
        '''
        _equal_mapping returns null when keys match.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare matching mapping keys.
        assert check._equal_mapping({'id': 'a'}, {'id': 'a'}) is None

    # * test: equal_mapping_mismatch
    def test_equal_mapping_mismatch(self, check):
        '''
        _equal_mapping returns the scalar mismatch text when values differ.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Compare differing mapping values.
        assert check._equal_mapping({'id': 'a'}, {'id': 'b'}) == "'a' != 'b'."

    # * test: equal_keyed_match
    def test_equal_keyed_match(self, check):
        '''
        _equal_keyed returns null when keyed items match.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Match one object to its item fields by id.
        obj = type('Obj', (), {'id': 'a'})()
        assert check._equal_keyed(
            [obj],
            {
                'key': 'id',
                'items': {
                    'a': {
                        'id': 'a',
                    },
                },
            },
        ) is None

    # * test: equal_keyed_mismatch
    def test_equal_keyed_mismatch(self, check):
        '''
        _equal_keyed returns when an item field differs.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Mismatch one object against item fields by id.
        obj = type('Obj', (), {'id': 'a'})()
        assert check._equal_keyed(
            [obj],
            {
                'key': 'id',
                'items': {
                    'a': {
                        'id': 'b',
                    },
                },
            },
        ) == "'a' != 'b'."

    # * test: expect_code_match
    def test_expect_code_match(self, check):
        '''
        _expect_code returns null when the raised code matches.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Raise an exception whose error_code matches.
        def raise_code():
            error = Exception()
            error.error_code = 'PHASE_CHECK_FAILED'
            raise error

        assert check._expect_code(
            raise_code,
            'PHASE_CHECK_FAILED',
            'absent',
        ) is None

    # * test: expect_code_mismatch
    def test_expect_code_mismatch(self, check):
        '''
        _expect_code returns when the raised code differs.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Raise an exception whose error_code differs.
        def raise_code():
            error = Exception()
            error.error_code = 'PHASE_STEP_FAILED'
            raise error

        assert check._expect_code(
            raise_code,
            'PHASE_CHECK_FAILED',
            'absent',
        ) == "'PHASE_STEP_FAILED' != 'PHASE_CHECK_FAILED'."

    # * test: reject_call_raises
    def test_reject_call_raises(self, check):
        '''
        _reject_call raises CHECK_CALL_INVALID with the supplied message.

        :param check: The constructed Check.
        :type check: Check
        '''

        # Raise the uncatalogued bad-call code.
        message = 'codes compares two error-code strings.'
        with pytest.raises(ServiceError) as exc_info:
            check._reject_call(message)
        assert exc_info.value.error_code == 'CHECK_CALL_INVALID'
        assert exc_info.value.message == message
