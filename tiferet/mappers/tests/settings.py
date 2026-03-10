"""Tiferet Mapper Test Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ...assets import TiferetError
from ..settings import Aggregate, TransferObject

# *** classes

# ** class: MapperAssertions
class MapperAssertions:
    '''
    Internal mixin providing shared assertion helpers for mapper tests.
    '''

    # * attribute: equality_fields
    equality_fields: list[str] = []

    # * attribute: field_normalizers
    field_normalizers: dict[str, callable] = {}

    # * method: assert_model_matches
    def assert_model_matches(
        self,
        model,
        sample: dict,
        equality_fields: list[str] = None,
        field_normalizers: dict = None,
    ):
        '''
        Compare model attributes against a sample data dict using configured fields and normalizers.

        :param model: The model instance to check.
        :param sample: The expected values dict.
        :type sample: dict
        :param equality_fields: Fields to compare (defaults to self.equality_fields).
        :type equality_fields: list[str]
        :param field_normalizers: Per-field normalizers (defaults to self.field_normalizers).
        :type field_normalizers: dict
        '''

        # Use defaults from the class if not provided.
        equality_fields = equality_fields or self.equality_fields
        field_normalizers = field_normalizers or self.field_normalizers

        # Compare each field.
        for field in equality_fields:
            if field not in sample:
                continue

            expected = sample[field]
            actual = getattr(model, field, None)

            normalizer = field_normalizers.get(field)
            if normalizer:
                expected = normalizer(expected)
                actual = normalizer(actual)

            assert actual == expected, (
                f"Mismatch on field '{field}':\n"
                f"  expected: {expected!r}\n"
                f"  actual:   {actual!r}"
            )

    # * method: assert_nested_list_matches
    def assert_nested_list_matches(
        self,
        actual_list: list,
        expected_list: list | dict,
        key_field: str = 'attribute_id',
        compare_fields: list[str] = None,
    ):
        '''
        Helper for comparing lists of domain objects (e.g. services) by key.

        :param actual_list: The list of actual domain objects.
        :type actual_list: list
        :param expected_list: The expected list or dict keyed by key_field.
        :type expected_list: list | dict
        :param key_field: The field to use as comparison key.
        :type key_field: str
        :param compare_fields: Which fields to check per item.
        :type compare_fields: list[str]
        '''

        # Default to empty compare_fields (will use all non-private fields).
        if compare_fields is None:
            compare_fields = []

        # Index actual items by key.
        actual_by_key = {getattr(item, key_field): item for item in actual_list}

        # Index expected items by key.
        if isinstance(expected_list, dict):
            expected_by_key = expected_list
        else:
            expected_by_key = {getattr(item, key_field): item for item in expected_list}

        # Assert key sets match.
        assert set(actual_by_key) == set(expected_by_key), "Key sets differ"

        # Compare fields for each key.
        for key, expected in expected_by_key.items():
            actual = actual_by_key[key]
            fields = compare_fields or [f for f in vars(expected) if not f.startswith('_')]
            for f in fields:
                if f == key_field:
                    continue
                va = getattr(actual, f, None)
                ve = getattr(expected, f, None)
                assert va == ve, f"Nested mismatch at {key}.{f}: {va!r} != {ve!r}"


# ** class: AggregateTestBase
class AggregateTestBase(MapperAssertions):
    '''
    Base class for testing Aggregate components.

    Subclasses define:
    - aggregate_cls          — the Aggregate class under test
    - sample_data            — aggregate-format sample data
    - equality_fields        — fields to compare
    - field_normalizers      — optional per-field normalizers
    - set_attribute_params   — tuples of (attr, value, expect_error_code | None)
    '''

    # * attribute: aggregate_cls
    aggregate_cls: type[Aggregate] = None

    # * attribute: sample_data
    sample_data: dict = {}

    # * attribute: set_attribute_params
    set_attribute_params: list[tuple[str, any, str | None]] = []

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> Aggregate:
        '''
        Create an aggregate from data. Override for custom new() signatures.

        :param data: The data to create from (defaults to self.sample_data).
        :type data: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Create an aggregate using the standard Aggregate.new factory.
        return Aggregate.new(self.aggregate_cls, **(data or self.sample_data))

    # * fixture: aggregate
    @pytest.fixture
    def aggregate(self):
        '''
        Fixture providing an aggregate instance from sample_data.
        '''

        # Skip if no aggregate class is defined.
        if not self.aggregate_cls:
            pytest.skip("aggregate_cls not defined")

        # Create and return the aggregate.
        return self.make_aggregate()

    # * method: test_new
    def test_new(self, aggregate):
        '''
        Verify aggregate instantiation and field values match sample_data.
        '''

        # Assert the aggregate is the correct type.
        assert isinstance(aggregate, self.aggregate_cls)

        # Assert the aggregate fields match the sample data.
        self.assert_model_matches(aggregate, self.sample_data)

    # * method: test_set_attribute
    def test_set_attribute(self, aggregate, attr, value, expect_error_code):
        '''
        Parametrized test for set_attribute (valid and invalid).
        Parametrization is handled by conftest.pytest_generate_tests.
        '''

        # If an error is expected, verify the correct error code is raised.
        if expect_error_code:
            with pytest.raises(TiferetError) as exc_info:
                aggregate.set_attribute(attr, value)
            assert exc_info.value.error_code == expect_error_code

        # Otherwise verify the attribute was updated.
        else:
            aggregate.set_attribute(attr, value)
            assert getattr(aggregate, attr) == value


# ** class: TransferObjectTestBase
class TransferObjectTestBase(MapperAssertions):
    '''
    Base class for testing TransferObject components.

    Subclasses define:
    - transfer_cls            — the TransferObject class under test
    - aggregate_cls           — the target Aggregate class
    - sample_data             — YAML-format sample data for from_data
    - aggregate_sample_data   — aggregate-format expected data (defaults filled in)
    - equality_fields         — fields to compare on mapped results
    - field_normalizers       — optional per-field normalizers
    - map_kwargs              — extra kwargs to pass to .map()
    '''

    # * attribute: transfer_cls
    transfer_cls: type[TransferObject] = None

    # * attribute: aggregate_cls
    aggregate_cls: type[Aggregate] = None

    # * attribute: sample_data
    sample_data: dict = {}

    # * attribute: aggregate_sample_data
    aggregate_sample_data: dict = {}

    # * attribute: map_kwargs
    map_kwargs: dict = {}

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> Aggregate:
        '''
        Create an aggregate for from_model / round_trip tests.
        Override for custom new() signatures.

        :param data: The data to create from (defaults to self.aggregate_sample_data).
        :type data: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Create an aggregate using the standard Aggregate.new factory.
        return Aggregate.new(self.aggregate_cls, **(data or self.aggregate_sample_data))

    # * fixture: aggregate
    @pytest.fixture
    def aggregate(self):
        '''
        Fixture providing an aggregate instance from aggregate_sample_data.
        '''

        # Skip if no aggregate class is defined.
        if not self.aggregate_cls:
            pytest.skip("aggregate_cls not defined")

        # Create and return the aggregate.
        return self.make_aggregate()

    # * method: test_map
    def test_map(self):
        '''
        Verify TransferObject.from_data -> map() produces a valid aggregate.
        '''

        # Skip if no transfer class is defined.
        if not self.transfer_cls:
            pytest.skip("transfer_cls not defined")

        # Create a transfer object from YAML-format sample data.
        yaml_obj = TransferObject.from_data(self.transfer_cls, **self.sample_data)

        # Map to an aggregate.
        mapped = yaml_obj.map(**self.map_kwargs)

        # Assert the mapped aggregate is the correct type and matches expected data.
        assert isinstance(mapped, self.aggregate_cls)
        self.assert_model_matches(mapped, self.aggregate_sample_data)

    # * method: test_from_model
    def test_from_model(self, aggregate):
        '''
        Verify aggregate -> TransferObject conversion.
        '''

        # Skip if no transfer class is defined.
        if not self.transfer_cls:
            pytest.skip("transfer_cls not defined")

        # Convert the aggregate to a transfer object.
        yaml_obj = self.transfer_cls.from_model(aggregate)

        # Assert the result is the correct type.
        assert isinstance(yaml_obj, self.transfer_cls)

    # * method: test_round_trip
    def test_round_trip(self, aggregate):
        '''
        Verify aggregate -> TransferObject -> aggregate round-trip.
        '''

        # Skip if no transfer class is defined.
        if not self.transfer_cls:
            pytest.skip("transfer_cls not defined")

        # Convert aggregate to transfer object and back.
        yaml_obj = self.transfer_cls.from_model(aggregate)
        round_tripped = yaml_obj.map(**self.map_kwargs)

        # Assert the round-tripped aggregate matches expected data.
        assert isinstance(round_tripped, self.aggregate_cls)
        self.assert_model_matches(round_tripped, self.aggregate_sample_data)
