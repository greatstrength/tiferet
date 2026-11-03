"""Tiferet Utils Stage Tests"""

# *** imports

# ** core
import logging
import os
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.interfaces.tester_stage import StageService
from tiferet.utils.tester_stage import Stage, STAGE_CALL_INVALID

# *** fixtures

# ** fixture: stage
@pytest.fixture
def stage():
    '''
    Provide an arranged stage that is closed after the case, also when it fails.

    :return: An arranged Stage.
    :rtype: Stage
    '''

    # Arrange the stage, yield it, and close it.
    stage = Stage()
    stage.arrange()
    try:
        yield stage
    finally:
        stage.close()

# *** testers

# ** tester: test_stage
@use_tester(
    type='generic',
    target_cls=Stage,
)
class TestStage:
    '''
    Tests for the Stage utility.
    '''

    # * test: new
    def test_new(self):
        '''
        Assert a new stage is an unarranged StageService.
        '''

        # Construct the subject with no arguments.
        built = Stage()

        # Assert the type and the null fields.
        assert isinstance(built, StageService)
        assert built.directory is None
        assert built.handler is None
        assert built.root_level is None

    # * test: path_creates_nothing
    def test_path_creates_nothing(self, stage):
        '''
        Assert path joins parts under the directory and creates nothing.

        :param stage: The arranged stage.
        :type stage: Stage
        '''

        # Join no parts, one part, and two parts.
        directory = stage.path()
        single = stage.path('does_not_exist.txt')
        nested = stage.path('nonexistent_dir', 'file.txt')

        # Assert the joins and the empty directory.
        assert Path(directory).is_dir() is True
        assert single == str(Path(directory, 'does_not_exist.txt'))
        assert nested == str(Path(directory, 'nonexistent_dir', 'file.txt'))
        assert os.listdir(directory) == []

    # * test: segments_stay_inside
    @pytest.mark.parametrize('part', ['', '.', '..', '/etc', 'a/b', 3])
    def test_segments_stay_inside(self, stage, part):
        '''
        Assert a part that is not one relative segment is rejected.

        :param stage: The arranged stage.
        :type stage: Stage
        :param part: The rejected part.
        :type part: Any
        '''

        # Call path with the part.
        with pytest.raises(ServiceError) as exc_info:
            stage.path(part)
        assert exc_info.value.error_code == STAGE_CALL_INVALID
        assert repr(part) in exc_info.value.message

        # Call write with the part.
        with pytest.raises(ServiceError):
            stage.write(part, 'x')

        # Assert nothing was written.
        assert os.listdir(stage.path()) == []

    # * test: write_read_exists
    def test_write_read_exists(self, stage):
        '''
        Assert write, read, and exists round-trip utf-8 text without newline translation.

        :param stage: The arranged stage.
        :type stage: Stage
        '''

        # Check, write, read, and check again.
        before = stage.exists('config.yaml')
        written = stage.write('config.yaml', 'root: {}\r\n')
        written_bytes = Path(written).read_bytes()
        text = stage.read('config.yaml')
        after = stage.exists('config.yaml')

        # Overwrite one child and write a second.
        stage.write('config.yaml', 'root: 1\n')
        stage.write('dispatch.json', '{}')
        overwritten = stage.read('config.yaml')
        second = stage.exists('dispatch.json')

        # Assert the observations.
        assert before is False
        assert after is True
        assert second is True
        assert written_bytes == 'root: {}\r\n'.encode('utf-8')
        assert text == 'root: {}\r\n'
        assert overwritten == 'root: 1\n'

        # Read a missing child.
        with pytest.raises(ServiceError):
            stage.read('missing.txt')

        # Write bytes.
        with pytest.raises(ServiceError):
            stage.write('data.bin', b'bytes')

    # * test: records_and_message
    def test_records_and_message(self, stage):
        '''
        Assert records returns plain dicts in emission order and message selects by level and index.

        :param stage: The arranged stage.
        :type stage: Stage
        '''

        # Log on the root and a named logger.
        root = logging.getLogger()
        root.debug('Executing SampleEvent')
        logging.getLogger('tiferet.stage_probe').debug('named')
        try:
            raise ValueError('boom')
        except ValueError:
            root.error('Failed SampleEvent', exc_info=True)
        root.log(25, 'custom')

        # Read the records and one message.
        stored = stage.records()
        line = stage.message('DEBUG', 1)

        # Log again and read a fresh list.
        root.info('later')
        fresh = stage.records()

        # Assert the observations.
        assert stored == [
            {'level': 'DEBUG', 'message': 'Executing SampleEvent', 'error': False, 'logger': 'root'},
            {'level': 'DEBUG', 'message': 'named', 'error': False, 'logger': 'tiferet.stage_probe'},
            {'level': 'ERROR', 'message': 'Failed SampleEvent', 'error': True, 'logger': 'root'},
            {'level': 'Level 25', 'message': 'custom', 'error': False, 'logger': 'root'},
        ]
        assert line == 'named'
        assert len(stored) == 4
        assert fresh[-1]['message'] == 'later'

        # Reject a bad level, a negative index, a bool index, and an index past the end.
        for level, index in [('TRACE', 0), ('DEBUG', -1), ('DEBUG', True), ('ERROR', 1)]:
            with pytest.raises(ServiceError):
                stage.message(level, index)

    # * test: error_flag_is_exc_info_not_none
    def test_error_flag_is_exc_info_not_none(self, stage):
        '''
        Assert the error flag is exc_info is not None, not the truth of exc_info.

        :param stage: The arranged stage.
        :type stage: Stage
        '''

        # Log at ERROR with each exc_info form.
        root = logging.getLogger()
        root.error('no exc_info')
        root.error('false', exc_info=False)
        root.error('true without an exception', exc_info=True)
        try:
            raise ValueError('boom')
        except ValueError:
            root.error('true with an exception', exc_info=True)

        # Assert the message and error pairs.
        assert [(record['message'], record['error']) for record in stage.records()] == [
            ('no exc_info', False),
            ('false', True),
            ('true without an exception', True),
            ('true with an exception', True),
        ]

    # * test: close_restores_and_removes
    def test_close_restores_and_removes(self):
        '''
        Assert close restores the root handlers and level and removes the directory.
        '''

        # Set the root to WARNING and record its handlers.
        root = logging.getLogger()
        original_level = root.level
        root.setLevel(logging.WARNING)
        handlers = list(root.handlers)
        try:

            # Arrange, read the directory, and write a child.
            built = Stage()
            built.arrange()
            directory = built.path()
            built.write('left.txt', 'x')

            # Read the arranged level and raise the root to ERROR.
            arranged_level = root.level
            root.setLevel(logging.ERROR)

            # Close twice.
            built.close()
            built.close()

            # Assert the restored state.
            assert arranged_level == logging.DEBUG
            assert Path(directory).exists() is False
            assert root.handlers == handlers
            assert root.level == logging.WARNING
        finally:
            root.setLevel(original_level)

    # * test: unarranged_stage_rejects_calls
    def test_unarranged_stage_rejects_calls(self):
        '''
        Assert an unarranged, re-arranged, or closed stage rejects calls.
        '''

        # Call path on an unarranged stage.
        built = Stage()
        with pytest.raises(ServiceError):
            built.path()

        # Arrange twice.
        built.arrange()
        try:
            with pytest.raises(ServiceError):
                built.arrange()
        finally:

            # Close, then read the records.
            built.close()
        with pytest.raises(ServiceError):
            built.records()
