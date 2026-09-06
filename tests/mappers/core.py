"""Shared support for bespoke mapper behavior tests."""

# *** imports

# ** infra
import pytest

# *** classes

# ** class: mapper_test_support
class MapperTestSupport:
    '''
    Provides aggregate construction and fixtures for mapper assertions beyond
    the generated tester factories' declared contract.
    '''

    # * attribute: aggregate_cls
    aggregate_cls: type

    # * attribute: sample_data
    sample_data: dict = {}

    # * attribute: aggregate_sample_data
    aggregate_sample_data: dict = {}

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None):
        '''
        Construct the declared aggregate from supplied or sample data.

        :param data: Optional construction data.
        :type data: dict
        :return: The constructed aggregate.
        :rtype: object
        '''

        # Prefer explicit data, then aggregate-shaped sample data.
        data = data if data is not None else self.aggregate_sample_data or self.sample_data

        # Construct and return the declared aggregate.
        return self.aggregate_cls(**data)

    # * fixture: aggregate
    @pytest.fixture
    def aggregate(self):
        '''
        Provide a fresh aggregate for a bespoke behavior assertion.

        :return: The constructed aggregate.
        :rtype: object
        '''

        # Create and return the test aggregate.
        return self.make_aggregate()
