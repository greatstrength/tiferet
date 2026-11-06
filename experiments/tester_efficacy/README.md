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

## Managed live-instance failures (group3)

The experimental reserved action `target: $r.driver`, `method: patch_raises`, `kwargs: {method: operate, module_path: builtins, class_name: OSError, message: injected}` installs a failure after the actual instance exists. It does not call the method. Call its owning consumer in the next step and verify the captured error and cause. Scope restoration belongs to both phase and compiled-feature run entries, not an arranged spare mock. All syntax and limitations are documented in docs/core/testing.md.

Run core experiments using `PYTHONPATH=/path/to/tiferet-ly:$PYTHONPATH python -m pytest -q experiments/tester_efficacy/tests`. They cover restoration on pass, assertion failure, execution failure, KeyboardInterrupt and partially completed setup through both runtime entries; stage directory and root logger restoration; LIFO restoration of a preexisting own callable; rejected targets/specifications; cleanup failures; disconnected-target and swallowed-error mutants. Group3 itself includes no module/class spy feature; group4 below adds that distinct scope.

Actual H5 proofs are isolated under consumer_h5 because the framework does not require PyTables. With the existing H5 project environment active and this checkout plus the actual H5 source on PYTHONPATH, run `python -m pytest -q experiments/tester_efficacy/consumer_h5/tests/test_live_h5_patch.py`. Its YAML counterpart is run with `run_test_module("experiments/tester_efficacy/consumer_h5/tests/test_live_h5_patch.py")`. Do not count a missing consumer environment as a passing conversion or silently skip it.

Consumer validation uses tiferet-h5 build commit c1e29b7fce1519965caac5770d060d184d081e0f with PyTables3.11.1. It injects NodeError into the live File.create_group reached by H5Client.create_group -> _ensure_parent_groups and HDF5ExtError into File.copy_children reached by H5Client.compact. Both require the original ServiceError code, exact exception class/message and chained cause. This consumer revision has no public ensure_parent_groups method; the older probe spelling is not claimed as a successful literal port. Post-restoration real operations succeed, class descriptors are unchanged, and another actual File remains usable. Reversible mutants patch a disconnected real File or swallow the actual consumer's ServiceError; both must fail the efficacy gate. These experiments demonstrate feasibility on that exact consumer revision, not wholesale migration or retirement of H5 pytest coverage.

The original H5 `test_compact_copy_failure_raises` assertion passes but its pytest monkeypatch teardown errors after File.close has cleared the instance dictionary (`AttributeError: File has no attribute copy_children`). This was reproduced unchanged with installed released Tiferet2.2.2b1, not just this feature build; no H5 test is modified here. The new restoration uses dictionary pop with a missing-key default and has explicit real-File-close-before-restoration regressions. This does not claim the external native pytest suite is green or silently remove that gate.

## Scoped forwarding spies (group4)

The `spy_calls` syntax and serial module/class lifetime limits are in docs/core/testing.md. It records real calls with original object references, not replacement behavior. Existing call checks observe named aliases without adding spies to constructor-injected mocks. Group3 live-instance injection remains distinct and shares the same restoration stack; layering is tested in both orders.

Core descriptor/module tests are in tests/test_spies.py and its YAML counterpart. Actual Ly proofs are isolated under consumer_ly because the framework does not depend on PLY. With the existing Ly environment active, this checkout and Ly230047b81bdc8594098b3992a0a95bda30f65724 on PYTHONPATH, run `python -m pytest -q experiments/tester_efficacy/consumer_ly/tests`. For a runner-only proof, call run_test_module on consumer_ly/tests/test_ly_spies.py. The imported consumer_ly/fixtures.py does not import or invoke pytest: it adapts the original arithmetic catalogue fixture to absolute temporary paths without changing CWD, DI production code or Ly source.

Four YAML consumer proofs cover unknown grammar with zero PLY lex calls, each feature's non-dict rewrites rejection with exactly the rewrites violation and zero lexer/parser entries, and a raw parse call preserving the exact lexeme-list identity and result3. The last is a focused forwarding proof, not a claim that the full original rendered/raw matrix has been migrated. Original pytest gates remain intact. Reversible extra-call mutations preserve the expected error while violating zero-call checks; copying the forwarded stream preserves parse result3 but violates identity; dropping it fails the consumer gate. These experiments are local build validation, not capabilities of the unchanged published beta.
