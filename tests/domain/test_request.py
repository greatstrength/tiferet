"""Tests for Tiferet Domain Request"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.request import Request

# *** constants

# ** constant: request_sample_data
REQUEST_SAMPLE_DATA = {
    'session_id': 'fixed-session',
    'feature_id': 'calc.add',
    'headers': {'h': '1'},
    'data': {'a': 1},
}

# *** testers

# ** tester: test_request
@use_tester(
    type='domain',
    target_cls=Request,
    sample_data=REQUEST_SAMPLE_DATA,
    equality_fields=['session_id', 'feature_id', 'headers', 'data'],
)
class TestRequest:
    '''Tests for Request construction, defaults, and session_id derivation.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Request construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: defaults
    def test_defaults(self, test_ctx) -> None:
        '''Test that Request defaults headers/data to empty dicts and feature_id to None.'''

        request = test_ctx.make_target(data={})

        assert request.headers == {}
        assert request.data == {}
        assert request.feature_id is None

    # * test: session_id_auto_derived
    def test_session_id_auto_derived(self, test_ctx) -> None:
        '''Test that a session_id is auto-generated when not supplied.'''

        request = test_ctx.make_target(data={})

        assert isinstance(request.session_id, str)
        assert request.session_id
        assert test_ctx.make_target(data={}).session_id != request.session_id

    # * test: session_id_preserved
    def test_session_id_preserved(self, test_ctx) -> None:
        '''Test that an explicit session_id is preserved.'''

        request = test_ctx.make_target()

        assert request.session_id == 'fixed-session'

    # * test: model_dump_round_trip
    def test_model_dump_round_trip(self, test_ctx) -> None:
        '''Test that a Request round-trips through model_dump.'''

        request = test_ctx.make_target(data={'feature_id': 'calc.add', 'data': {'a': 1}})
        reloaded = Request(**request.model_dump())

        assert reloaded.feature_id == 'calc.add'
        assert reloaded.data == {'a': 1}
        assert reloaded.session_id == request.session_id
