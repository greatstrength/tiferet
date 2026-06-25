"""Tests for Tiferet Domain Request"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.request import Request

# *** tests

# ** test: request_defaults
def test_request_defaults() -> None:
    '''
    Test that Request defaults headers/data to empty dicts and feature_id to None.
    '''

    # Create a Request with no arguments.
    request = Request()

    # Assert the defaults.
    assert request.headers == {}
    assert request.data == {}
    assert request.feature_id is None

# ** test: request_session_id_auto_derived
def test_request_session_id_auto_derived() -> None:
    '''
    Test that a session_id is auto-generated when not supplied.
    '''

    # Create a Request without a session id.
    request = Request()

    # Assert a session id was generated.
    assert isinstance(request.session_id, str)
    assert request.session_id

    # Assert two requests receive distinct session ids.
    assert Request().session_id != request.session_id

# ** test: request_session_id_preserved
def test_request_session_id_preserved() -> None:
    '''
    Test that an explicit session_id is preserved.
    '''

    # Create a Request with an explicit session id.
    request = Request(session_id='fixed-session')

    # Assert the session id is preserved.
    assert request.session_id == 'fixed-session'

# ** test: request_construction_with_fields
def test_request_construction_with_fields() -> None:
    '''
    Test that Request stores supplied fields.
    '''

    # Create a fully-specified Request.
    request = Request(feature_id='calc.add', headers={'h': '1'}, data={'a': 1})

    # Assert the fields are stored.
    assert request.feature_id == 'calc.add'
    assert request.headers == {'h': '1'}
    assert request.data == {'a': 1}

# ** test: request_model_dump_round_trip
def test_request_model_dump_round_trip() -> None:
    '''
    Test that a Request round-trips through model_dump.
    '''

    # Create a Request and serialize it.
    request = Request(feature_id='calc.add', data={'a': 1})
    primitive = request.model_dump()

    # Reload the Request from the serialized data.
    reloaded = Request(**primitive)

    # Assert the round-trip preserves the fields.
    assert reloaded.feature_id == 'calc.add'
    assert reloaded.data == {'a': 1}
    assert reloaded.session_id == request.session_id
