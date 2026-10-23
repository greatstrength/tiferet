"""Tiferet Utils Stage Tests"""

# *** imports

# ** core
import inspect
import logging
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.interfaces import StageService
from tiferet.interfaces.core import Service, ServiceError
from tiferet.utils.tester_stage import STAGE_CALL_INVALID, Stage

# *** fixtures

# ** fixture: stage
@pytest.fixture
def stage() -> Stage:
    '''
    Provide an arranged stage that is closed after the test.

    :return: The arranged stage.
    :rtype: Stage
    '''

    # Arrange, hand over, then close even when the test failed.
    stage = Stage()
    stage.arrange()
    yield stage
    stage.close()

# *** tests

# ** test: stage_service_contract
def test_stage_service_contract() -> None:
    '''StageService is a Service with the eight abstract stage methods.'''

    # The contract is the interface. The util implements it.
    assert issubclass(StageService, Service)
    assert StageService.__abstractmethods__ == {
        'arrange',
        'close',
        'path',
        'write',
        'read',
        'exists',
        'records',
        'message',
    }
    assert list(inspect.signature(StageService.path).parameters) == ['self', 'parts']
    assert list(inspect.signature(StageService.message).parameters) == ['self', 'level', 'index']
    assert issubclass(Stage, StageService)
    with pytest.raises(TypeError):
        StageService()

# ** test: path_creates_nothing
def test_path_creates_nothing(stage: Stage) -> None:
    '''path joins parts under the directory and creates nothing.'''

    # No args is the directory. A child or a missing parent is not created.
    directory = Path(stage.path())
    assert directory.is_dir()
    assert stage.path('does_not_exist.txt') == str(directory / 'does_not_exist.txt')
    assert stage.path('nonexistent_dir', 'file.txt') == str(directory / 'nonexistent_dir' / 'file.txt')
    assert list(directory.iterdir()) == []

# ** test: segments_stay_inside
@pytest.mark.parametrize('part', ['', '.', '..', '/etc', 'a/b', 3])
def test_segments_stay_inside(stage: Stage, part) -> None:
    '''Empty, dot, dot-dot, absolute, separated, and non-string parts are rejected.'''

    # Each is a stage-call error, and nothing is written.
    with pytest.raises(ServiceError) as caught:
        stage.path(part)
    assert caught.value.error_code == STAGE_CALL_INVALID
    with pytest.raises(ServiceError):
        stage.write(part, 'x')
    assert list(Path(stage.path()).iterdir()) == []

# ** test: write_read_exists
def test_write_read_exists(stage: Stage) -> None:
    '''write stores utf-8 bytes, read returns raw text, exists reports presence.'''

    # Before and after a write. Newlines are not translated.
    assert stage.exists('config.yaml') is False
    written = stage.write('config.yaml', 'root: {}\r\n')
    assert Path(written).read_bytes() == 'root: {}\r\n'.encode('utf-8')
    assert stage.read('config.yaml') == 'root: {}\r\n'
    assert stage.exists('config.yaml') is True

    # A second write overwrites. Two names coexist.
    stage.write('config.yaml', 'root: 1\n')
    stage.write('dispatch.json', '{}')
    assert stage.read('config.yaml') == 'root: 1\n'
    assert stage.exists('dispatch.json') is True

    # A missing name and bytes are stage-call errors.
    with pytest.raises(ServiceError):
        stage.read('missing.txt')
    with pytest.raises(ServiceError):
        stage.write('data.bin', b'bytes')

# ** test: records_and_message
def test_records_and_message(stage: Stage) -> None:
    '''records returns plain dicts in order; message selects by level and index.'''

    # A root record, a propagating named record, an error, and an unnamed level.
    logging.debug('Executing SampleEvent')
    logging.getLogger('tiferet.stage_probe').debug('named')
    try:
        raise ValueError('boom')
    except ValueError:
        logging.error('Failed SampleEvent', exc_info=True)
    logging.log(25, 'custom')
    stored = stage.records()
    assert stored == [
        {'level': 'DEBUG', 'message': 'Executing SampleEvent', 'error': False, 'logger': 'root'},
        {'level': 'DEBUG', 'message': 'named', 'error': False, 'logger': 'tiferet.stage_probe'},
        {'level': 'ERROR', 'message': 'Failed SampleEvent', 'error': True, 'logger': 'root'},
        {'level': 'Level 25', 'message': 'custom', 'error': False, 'logger': 'root'},
    ]
    assert stage.message('DEBUG', 1) == 'named'

    # A list stored earlier does not grow.
    logging.info('later')
    assert len(stored) == 4
    assert stage.records()[-1]['message'] == 'later'

    # A bad level, a bad index, and a missing index are stage-call errors.
    for level, index in (('TRACE', 0), ('DEBUG', -1), ('DEBUG', True), ('ERROR', 1)):
        with pytest.raises(ServiceError):
            stage.message(level, index)

# ** test: error_flag_is_exc_info_not_none
def test_error_flag_is_exc_info_not_none(stage: Stage) -> None:
    '''error is record.exc_info is not None, the literal rule.'''

    # No exc_info leaves the record's exc_info None. Any passed exc_info does not.
    logging.error('no exc_info')
    logging.error('false', exc_info=False)
    logging.error('true without an exception', exc_info=True)
    try:
        raise ValueError('boom')
    except ValueError:
        logging.error('true with an exception', exc_info=True)
    assert [(item['message'], item['error']) for item in stage.records()] == [
        ('no exc_info', False),
        ('false', True),
        ('true without an exception', True),
        ('true with an exception', True),
    ]

# ** test: close_restores_and_removes
def test_close_restores_and_removes() -> None:
    '''close detaches the handler, restores the root level, and removes the directory.'''

    # Arrange over a WARNING root.
    root = logging.getLogger()
    previous = root.level
    root.setLevel(logging.WARNING)
    handlers = list(root.handlers)
    try:
        stage = Stage()
        stage.arrange()
        directory = Path(stage.path())
        stage.write('left.txt', 'x')
        assert root.level == logging.DEBUG
        root.setLevel(logging.ERROR)

        # Close twice. The second is a no-op.
        stage.close()
        stage.close()
        assert not directory.exists()
        assert root.handlers == handlers
        assert root.level == logging.WARNING
    finally:
        root.setLevel(previous)

# ** test: unarranged_stage_rejects_calls
def test_unarranged_stage_rejects_calls() -> None:
    '''An unarranged or closed stage rejects observations, and arranges once.'''

    # Before arrange.
    stage = Stage()
    with pytest.raises(ServiceError):
        stage.path()

    # After close.
    stage.arrange()
    with pytest.raises(ServiceError):
        stage.arrange()
    stage.close()
    with pytest.raises(ServiceError):
        stage.records()
