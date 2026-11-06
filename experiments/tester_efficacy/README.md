# Tester draft efficacy experiments

These build-only experiments are separate from graduated suites. No new tester field or target permission is implied for those suites.

## Arranged mock raising

With the project virtual environment active, run `python -m pytest -q experiments/tester_efficacy/tests/test_arranged_raises.py`. Run the YAML counterpart with `run_test_module("experiments/tester_efficacy/tests/test_arranged_raises.py")` from `tiferet.blueprints.tester`.

A method declaration such as `return_value: {read: {raises: {module_path: builtins, class_name: ValueError, message: driver failed}}}` already configures a mock method to raise. The consumer must actually receive that arranged mock. `context: true` returns the same mock from `__enter__`; the Python regression verifies exception identity and traceback reaching `__exit__`. Omitting the message uses the exception class directly. Mixed return/raise data and malformed exception specifications fail arrangement.

This does NOT patch an existing live collaborator. A separate arranged `tables.File` mock does not replace the File created inside H5Client. TH51 remains blocked pending scoped live-instance patching. No top-level `side_effect` field is added.

The automated nonraising mutant removes `_arrange_raises` behavior and requires the actual consumer scenario to fail. Experiments are invoked explicitly; project-default pytest/YAML suites are not replaced.

## Runtime assignment on the actual Ly model

These consumer experiments require the existing Ly source on `PYTHONPATH`; they do not add Ly as a framework dependency, skip silently, vendor its model, or edit that repository. With the project virtual environment active, run `PYTHONPATH=/path/to/tiferet-ly:$PYTHONPATH python -m pytest -q experiments/tester_efficacy/tests/test_assignment.py`. The YAML command is `run_test_module("experiments/tester_efficacy/tests/test_assignment.py")` with the same import path.

The model used for validation is `tiferet_ly.domain.layout.LayoutProfile` at Ly commit `230047b81bdc8594098b3992a0a95bda30f65724`; its source pytest is `tests/domain/test_layout.py::test_layout_profile_rejects_non_positive_tab_size_assignment`. Its `tab_size` has default 4 and `ge=1`, inherited assignment validation. A new real model is stored as `profile`, its initial value read, and `target: $r.profile`, `method: __setattr__`, `args: [tab_size, 0]`, `raises: true`, `as: assignment` invokes the actual setter. Type/message checks inspect the captured ValidationError and a fields check inspects that same profile, not the setter's return. A valid assignment stores 8 and returns None. Zero, negative and false values are rejected and leave this model at 4.

There is no new reserved `setattr` action. `target: self` remains limited to the existing `new`/`handle` actions. This result does not promise rollback for every Pydantic validator or arbitrary Python setter. The reversible mutation disables this real model's assignment validation and clears cached setters; all three rejecting cases must fail. No consumer source files are changed.
