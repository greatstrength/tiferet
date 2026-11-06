"""Consumer proof using actual H5Client and real PyTables File instances."""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables
from tiferet_h5.utils.h5 import H5Client

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime, run_test_module
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import PhaseRuntimeContext
from tiferet.domain.tester_phase import Execution
from tiferet.interfaces import ServiceError
from tiferet.mappers.tester_phase import TestConfigObject

# *** functions

# ** function: consumer_case
def consumer_case(method):
    """Build a patch then invoke the real H5 owner, not the File directly.

    :param method: The live method name under test.
    :type method: Any
    """

    compact = method == 'copy_children'
    return {
        'conditions': {},
        'execute': [
            {'target': '$r.file', 'method': 'patch_raises', 'kwargs': {
                'method': method, 'module_path': 'tables',
                'class_name': 'HDF5ExtError' if compact else 'NodeError', 'message': 'injected',
            }},
            {'target': '$r.client', 'method': 'compact' if compact else 'create_group',
             'args': [] if compact else ['/missing/parent/leaf'], 'raises': True, 'as': 'failure'},
        ],
        'assert': [
            {'check': 'error_code', 'outcome': 'failure',
             'error_code': 'H5_COMPACT_FAILED' if compact else 'H5_GROUP_CREATE_FAILED'},
            {'outcome': 'failure', 'cause': {'module_path': 'tables',
             'class_name': 'HDF5ExtError' if compact else 'NodeError', 'message': 'injected'}},
        ],
    }

# ** function: run_consumer
def run_consumer(client, method):
    """Supply the exact live handle owned by H5Client to the runtime.

    :param client: The actual opened H5Client instance.
    :type client: Any
    :param method: The live method name under test.
    :type method: Any
    """

    runtime = build_phase_runtime(
        session=RequestContext(), tester_module_path='tiferet_h5.utils.h5', tester_class_name='H5Client',
    )
    runtime.session.data.update({'client': client, 'file': client.h5file})
    runtime.as_keys.update(['client', 'file'])
    model = TestConfigObject.model_validate(consumer_case(method)).map(id='h5.proof', name='h5.proof')
    runtime.run(model)
    return runtime

# *** tests

# ** test: actual_file_failure_and_restoration
@pytest.mark.parametrize('method', ['create_group', 'copy_children'])
def test_actual_file_failure_and_restoration(tmp_path, method):
    """Verify exact H5 error/cause, restoration and another real File's behavior.

    :param tmp_path: The temporary consumer file directory.
    :type tmp_path: Any
    :param method: The live method name under test.
    :type method: Any
    """

    descriptor = getattr(tables.File, method)
    with H5Client(tmp_path / 'actual.h5', mode='w') as client, H5Client(tmp_path / 'other.h5', mode='w') as other:
        file = client.h5file
        runtime = run_consumer(client, method)
        error = runtime.session.data['failure']
        assert isinstance(error, ServiceError)
        assert error.target_method == ('_ensure_parent_groups' if method == 'create_group' else 'compact')
        assert type(error.__cause__) is (tables.NodeError if method == 'create_group' else tables.HDF5ExtError)
        assert str(error.__cause__) == 'injected'
        assert method not in vars(file)
        assert getattr(file, method).__func__ is descriptor
        assert getattr(tables.File, method) is descriptor
        assert other.create_group('/unrelated')._v_pathname == '/unrelated'
        assert client.create_group('/restored')._v_pathname == '/restored'
        if method == 'copy_children':
            client.compact()

# ** test: disconnected_real_file_mutant_detected
@pytest.mark.parametrize('method', ['create_group', 'copy_children'])
def test_disconnected_real_file_mutant_detected(tmp_path, monkeypatch, method):
    """Injecting into a different real File must not satisfy the owner proof.

    :param tmp_path: The temporary consumer file directory.
    :type tmp_path: Any
    :param monkeypatch: The reversible pytest patch facility.
    :type monkeypatch: Any
    :param method: The live method name under test.
    :type method: Any
    """

    original = PhaseRuntimeContext._patch_instance_failure
    with H5Client(tmp_path / 'actual.h5', mode='w') as client, H5Client(tmp_path / 'spare.h5', mode='w') as spare:
        def disconnected(runtime, execution):
            target = runtime.session.data['file']
            runtime.session.data['file'] = spare.h5file
            try:
                return original(runtime, execution)
            finally:
                runtime.session.data['file'] = target
        monkeypatch.setattr(PhaseRuntimeContext, '_patch_instance_failure', disconnected)
        with pytest.raises(TiferetError) as caught:
            run_consumer(client, method)
        assert caught.value.error_code == 'PHASE_STEP_FAILED'
        assert method not in vars(spare.h5file)

# ** test: swallowed_actual_consumer_error_mutant_detected
@pytest.mark.parametrize('method', ['create_group', 'copy_children'])
def test_swallowed_actual_consumer_error_mutant_detected(tmp_path, monkeypatch, method):
    """Swallowing the real wrapped failure must make raises:true fail.

    :param tmp_path: The temporary consumer file directory.
    :type tmp_path: Any
    :param monkeypatch: The reversible pytest patch facility.
    :type monkeypatch: Any
    :param method: The live method name under test.
    :type method: Any
    """

    operation = 'compact' if method == 'copy_children' else 'create_group'
    original = getattr(H5Client, operation)
    def swallow(self, *args, **kwargs):
        try:
            return original(self, *args, **kwargs)
        except ServiceError:
            return None
    monkeypatch.setattr(H5Client, operation, swallow)
    with H5Client(tmp_path / 'actual.h5', mode='w') as client:
        with pytest.raises(TiferetError) as caught:
            run_consumer(client, method)
        assert caught.value.error_code == 'PHASE_STEP_FAILED'
        assert method not in vars(client.h5file)

# ** test: actual_h5_yaml_entry
def test_actual_h5_yaml_entry():
    """Run actual H5 creation, post-creation patching and consumer calls in YAML."""

    report = run_test_module(str(Path(__file__)))
    assert len(report['outcomes']) == 2
    assert not report['failures']

# ** test: closing_file_before_restoration_is_safe
@pytest.mark.parametrize('method', ['create_group', 'copy_children'])
def test_closing_file_before_restoration_is_safe(tmp_path, method):
    """A File clearing its dictionary on close must not break patch restoration.

    :param tmp_path: The temporary consumer file directory.
    :type tmp_path: pathlib.Path
    :param method: The live method being shadowed.
    :type method: str
    """

    client = H5Client(tmp_path / 'closed.h5', mode='w')
    client.__enter__()
    file = client.h5file
    runtime = build_phase_runtime(
        session=RequestContext(), tester_module_path='tiferet_h5.utils.h5', tester_class_name='H5Client',
    )
    runtime.session.data.update({'client': client, 'file': file})
    runtime.as_keys.update(['client', 'file'])
    try:
        runtime.handle_execution(Execution.model_validate(consumer_case(method)['execute'][0]))
    finally:
        client.__exit__(None, None, None)
        runtime.close_resources()
    assert method not in vars(file)
