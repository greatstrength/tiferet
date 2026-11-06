# Tester draft efficacy experiments

These build-only experiments are separate from graduated suites. No new tester field or target permission is implied for those suites.

## Arranged mock raising

With the project virtual environment active, run `python -m pytest -q experiments/tester_efficacy/tests/test_arranged_raises.py`. Run the YAML counterpart with `run_test_module("experiments/tester_efficacy/tests/test_arranged_raises.py")` from `tiferet.blueprints.tester`.

A method declaration such as `return_value: {read: {raises: {module_path: builtins, class_name: ValueError, message: driver failed}}}` already configures a mock method to raise. The consumer must actually receive that arranged mock. `context: true` returns the same mock from `__enter__`; the Python regression verifies exception identity and traceback reaching `__exit__`. Omitting the message uses the exception class directly. Mixed return/raise data and malformed exception specifications fail arrangement.

This does NOT patch an existing live collaborator. A separate arranged `tables.File` mock does not replace the File created inside H5Client. TH51 remains blocked pending scoped live-instance patching. No top-level `side_effect` field is added.

The automated nonraising mutant removes `_arrange_raises` behavior and requires the actual consumer scenario to fail. Experiments are invoked explicitly; project-default pytest/YAML suites are not replaced.
