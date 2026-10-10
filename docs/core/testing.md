# Tester Subdomain

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** October 7, 2026
**Version:** 2.2.0b1

## Overview

A unit test has two faces. In Python, `@use_tester` binds a `TesterObject` and injects `test_ctx` and `session`. In YAML, a test module under `tiferet_tests/` is a document whose only roots are `fixtures`, `tests`, and `testers`. A test, at the root or inside a tester, is a `Test`: a feature in purpose and a test in name. The model fields are `conditions`, `executes`, and `asserts`. The YAML keys stay `conditions`, `execute`, and `assert`.

`TestSessionContext` sees a `TestContext`, not a `FeatureContext`, when the module runner constructs the session. `@use_tester` still passes a positional `TesterContext`. The constructor switch is stated in Module run.

There is no `variables:` root. There is no separate tester vision file. Vision stays the class docstrings.

## The test module

A test module is one YAML document. It has three roots, in this order, and no others:

1. `fixtures` — named samples the tests and testers draw on.
2. `tests` — module-level tests.
3. `testers` — the attribution level. A tester holds `attributes` and `fixtures` and contains `tests`. It is not a fourth root and not a fourth phase.

Each root is a mapping. The key is the grammar snake name (`error_message`, `test_error`), not `Test*`. Omit an empty root. Do not write `{}` for an omitted root. No preamble keys.

A contained test is still the three YAML phases `conditions`, `execute`, `assert`. On the model those fields are `conditions`, `executes`, and `asserts`. Naming a root test from a tester does not move that test under the tester. A tester-local fixture is not promoted into the root `fixtures` mapping.

### File root

`tests/<rel>.py` maps to `tiferet_tests/<rel>.yml`, and only for `tests/**/test_*.py`. The extension is `.yml` only. `tests/domain/test_error.py` maps to `tiferet_tests/domain/test_error.yml`.

`conftest.py`, `__init__.py`, and `tests_int/` have no counterpart. Do not write the YAML under `tests/`. Do not delete the Python tests. The Error proof is `tiferet_tests/domain/test_error.yml`. Package counterparts beyond that file are later RFPs.

### The three phases

`Test` (`tiferet/domain/test.py`) extends `Feature`. The model fields are three, in this order: `conditions`, `executes`, `asserts`. `conditions` is a `Conditions`. `executes` is a list of `Execution`. `asserts` is a list of `Assertion`. These fields do not replace inherited `steps`. There is no fourth phase field, and no field named `execute`, `assert`, or `as`. None of them carries an alias.

`Conditions` is one object, not a list. It holds fixture names and a dict of `ArrangedMock`. `ArrangedMock` has `module_path`, `class_name`, and optional `context`. `return_value` stays data. `Execution` has `target` (`str` or `ExecutionTarget`), `method`, `args`, `kwargs`, `data_key`, and `raises`. `ExecutionTarget` is `module_path` plus exactly one of `class_name` or `attribute`. `Assertion` is one model. `check` is the discriminator. `is` and `type` are values of `check`, not field names. A comparison tree inside `fields` stays data.

The YAML keys stay `conditions`, `execute`, and `assert`. `as` maps onto `data_key`. RFP-035 (#1238) owns that mapping, including `as` onto `data_key`. This RFP does not add that mapping, and it adds no mapper module. The tester blueprint compiles these fields into `Feature.steps`. The handlers are not added to the default feature catalog, and they do not decorate `core.build_cache`. The closed contents of each phase are in the next section. There is no fourth phase.

### Phase contents

A phase is a closed mapping. This layer starts after `safe_load`. Anchors, aliases, and merge keys are already gone. The blueprint has already copied an aliased mapping. This layer mutates the copy it was given. It does not write back to the loaded document, and it does not call `safe_load` or `safe_dump`. `$fixture.`, `$r.`, and `$mock.` stay literal strings until a handler resolves them.

`conditions` accepts only `fixtures` and `mocks`. Omit an empty key. `conditions: {}` is legal. Omitting the phase is not. `fixtures` is a list of names, built in list order. Lookup is the tester-local `fixtures` mapping, then the root. A tester-local fixture is not promoted. A fixture entry, root or tester-local, is `module_path`, `class_name`, and `attributes`. The handler imports the module, gets the class, and calls it with `attributes` as keyword arguments. That is construction. It is not `eval`, and it is not a method named `new`. Attribute values are literals, lists, mappings, or a runtime ref. A nested mapping is data. It is not a second constructor, even if it contains `module_path`.

`mocks` is a mapping. Each value is `module_path`, `class_name`, and optional `return_value` and `context`. The handler builds `Mock(spec=imported class)`. It does not construct the class. `return_value` is a mapping of method name to a literal, YAML `null`, a `$fixture.` ref, a `$mock.` ref, or `{attributes: {name: value}}`. The handler sets `mock.<method>.return_value`. YAML `null` means the method returns `None`. `{attributes: ...}` builds an object whose attributes are those values. That is not a callable. A method may instead have `raises: {module_path, class_name, message}`. The handler raises that class, with that message when present. `return_value` and `raises` are mutually exclusive on one method. `context: true` makes `__enter__` return the mock. There is no `side_effect` key and no callable. Build fixtures first, then mocks. `$r.` is illegal in `conditions`. A mock name and a fixture name must not collide. `$mock.<name>` is the arranged mock. It is not `$fixture.`.

`execute` is a non-empty list. Each item's keys are only `target`, `method`, `args`, `kwargs`, `as`, and `raises`. `args` defaults to `[]`. `kwargs` defaults to `{}`. `raises` defaults to false. `target` is `self`, a fixture name, `$fixture.<name>`, `$r.<key>`, `$mock.<name>`, `{module_path, class_name}` for the class itself, or `{module_path, attribute}` for a module-level function. A bare name is a fixture, not a prior `as` key. A prior result is only `$r.<key>`.

Two method names are reserved harness actions. Every other name is a call. `new` and `handle` are not `getattr`. A real method with either name cannot be called through this dialect.

- `new` is legal only on `target: self`. It constructs the tester class from the tester's `module_path`, `class_name`, and `attributes`. It takes no `args` and no `kwargs`. `$fixture.` inside those attributes must already have been built. The instance is stored at `as`.
- `handle` is legal only on `target: self`. It calls `DomainEvent.handle` on the tester class, with `dependencies` equal to the mocks arranged in `conditions`, and with the step `kwargs` as the event arguments. It does not merge a hidden `sample_kwargs`. It does not construct an instance. There is no `dependencies` key on the step.
- Any other `method` is `getattr(target, method)(*args, **kwargs)`. A classmethod reached on an instance is still that call. `from_model` needs no special key. Refs in `args` and `kwargs` are resolved before the call.

`as` is the feature `data_key`. The tester blueprint compiles each execute item into one feature step. `as`, when present, is that step's `data_key`. The handler stores the return value in session data under that key. `$r.<as>` reads it. When `as` is omitted, the result is not addressable. Mutation methods return `None`. The check reads the instance already stored under an earlier `as`, not the `None` return. An execute item is not encoded as `EventFeatureStep.parameters`. Those values are strings. A fixture is not a string. `pass_on_error` is not set. That stores `None` and drops the error code.

`raises: true` catches. It does not check. The handler catches `Exception`, stores the exception under `as`, and does not fail the step. `as` is required when `raises` is true. If the call does not raise, the step fails. If `raises` is false, an exception fails the test. The code is not written on the execute item. `BaseException` is not caught. A following `error_code` check reads `outcome.error_code`.

`assert` is a non-empty list of named checks. Each item has exactly one check key, from the data checks or the harness checks below. No other check key is legal. `predicate`, `field_normalizers`, `contains`, `any`, `eval`, `code`, `python`, `body`, `side_effect`, `target_method`, `cause` as a key of its own outside the named check, `abstract_methods`, and `subclass_of` are illegal even when the value is data. A YAML Python tag is illegal. There is no stored callable, no class body, and no lambda in a YAML file.

Data checks:

- `equals`, `null`, `fields`, `error_code`, and `type` require `outcome`. `outcome` is an `as` key, `$r.<key>` for that same key, or a fixture name. If the name is both an `as` key and a fixture name, reject it. Do not guess.
- `equals` is `==` after ref resolution. YAML `null` under `equals` is rejected.
- `null: true` means the outcome `is None`. No other value is legal. This is not `equals: null`.
- `fields` compares named attributes. A scalar expected value is `==`. YAML `null` in a field means the attribute `== None`. A list expected value requires the same length, and each item is compared by this same rule, unless the expected value is `{key: <attr>, items: {<key>: <fields>}}`. That form matches a list of objects to a mapping keyed by `<attr>`, which replaces `field_normalizers`. A mapping expected value against an object compares each key as an attribute, recursively. Extra attributes on the object are ignored. A missing expected key fails. No callable normalizer. No index syntax. `message.1.lang` is not a key.
- `absent` requires `outcome` and is a list of names. On a mapping, each name must not be a key. On a model, each name must be missing from `model_dump()`.
- `error_code` reads `outcome.error_code` and compares it to a string. The string is the code, not a Python constant. A missing attribute fails the check. `ValidationError` has no `error_code`. Use `type` for it.
- `type` is `isinstance` against one imported `module_path` / `class_name`. `negate: true` means the outcome is not an instance of that class. A subclass passes unless negated. This is not `issubclass`.
- `is` is identity with an imported `module_path` / `class_name`, or with `builtin` set to `int`, `str`, `float`, `bool`, `list`, or `dict`. This is the live-type return. It is not `isinstance`.
- `message` is a substring of `str(outcome)`. It is not a general `contains`.
- `assert_called_once_with` requires `mock` and `method`, and must not have `outcome`. The value is `{args, kwargs}` for one call, `{times: N}`, or `{calls: [{args, kwargs}, ...]}`. `times` defaults to 1. `times: 0` means not called, and `args` must be omitted. `calls` is the exact sequence when two calls differ. There is no `assert_called`, `assert_any_call`, `call_count`, or `assert_not_called` key. Those are `times` and `calls`.

Harness checks. The harness owns the procedure and any throwaway class. The YAML file does not define a class or a lambda. Adoption selects the key. It does not spell a new one.

- `domain_contract: true` runs the DomainObject and model-error protocol: construction, extra field rejected as `ValidationError`, assignment failures, `unpack_validation_error`, `describe_model`, and `raise_for_validation` for unknown attribute and invalid value, with and without a model. The harness owns `TestDomainObject`, `TestIdentifiedObject`, and `Stub`.
- `mapper_contract: true` runs the Aggregate and TransferObject base protocol: construction, `set_attribute`, unknown attribute, invalid value, `model_validate`, `from_model`, `map`, and `to_primitive` for `to_data`, `to_model`, and an unknown role. The harness owns the two bases. An exclude set is a list in YAML. The harness compares it as a set. No `!!set`.
- `event_base: {module_path, class_name}` asserts the bound event subclasses that base and stores the injected service mock. One check covers a bare base-event tester.
- `parameters_required: {names: [...]}` runs the decorator matrix: missing, `None`, empty string, and a valid call. The code is `COMMAND_PARAMETER_REQUIRED`. The name is in the message. This is not a second meaning of a single `error_code` check.
- `service_contract` takes `abstracts`, `methods` (`name`, `params`, optional `defaults`, `annotations`, `returns`), and optional `absent`. It locks that table. It is not `assert_contract`. It also fails direct construction with `TypeError` when `abstracts` is non-empty.
- `middleware_chain` is one of `none`, `single`, `order`, `capture`, `intercept`, or `async`. The harness owns the wrappers. The check awaits on `async`. No async phase key. No lambda in the YAML file.
- `cause: {module_path, class_name, message}` reads `outcome.__cause__`. It is not a frame walk.

Runtime refs are whole values. `$fixture.<name>` is a fixture built in this test's `conditions`. `$r.<key>` is a `data_key` already stored by an earlier step of this test. `$mock.<name>` is an arranged mock. The name has no further dot. `$r.built.lang` is not a path. A ref is the entire scalar, not a substring. `An error occurred: $r.x` is a literal. Resolution does not call `eval` and does not call `evaluate_condition`. A missing name fails the step. It is not `None`. YAML `null` remains `None`.

Frame-derived `target_method` is not a check. A harness check that called `raise_for` itself would record the harness name, not the method under test. The two Python assertions stay in `tests/interfaces/test_core.py` because that file is not deleted. They are not YAML coverage.

One test compiles to one `Test`. The execute-phase items are the model's `executes`. The assert-phase items are the model's `asserts`. Each item is an `Execution` or an `Assertion`, not a dict. Step order is the conditions step, then each execute item, then each assert item. The three handlers are registered by the tester blueprint. They are not entries in a default feature catalog. They do not decorate `core.build_cache`. They are not dispatched through `AppSessionContext`. Assert items run in order. The first failure fails the test.

`TestContext` (`tiferet/contexts/test.py`) extends `FeatureContext` and declares `domain_type = Test` in its own namespace. `Feature` stays mapped to `FeatureContext`: `BaseContext.for_domain(Feature)` is `FeatureContext`.

`PhaseRuntime` (`tiferet/domain/test.py`) is the declared coordinates of one phase run: the class `new` and `handle` use, and the fixture specs. It does not build fixtures, arrange mocks, or touch a session. `PhaseRuntimeContext` declares `domain_type = PhaseRuntime` in its own namespace. `build_phase_runtime` builds that value and calls `BaseContext.from_domain`, so the registry returns `PhaseRuntimeContext`. It does not construct the context by hand, and it does not return the domain value. The tester context stores that callable and exposes `build_phase_runtime`. An absent callable is an unwired handler. The bound model stays immutable. Built fixtures, arranged mocks, and `as` keys are context attributes. A closed-set defect raises `ModelError`. A phase side effect raises `TiferetError`. A failed check raises `AssertionError`.

## Anchors, aliases, and merge

Anchors are load-time. `$r.` and `$fixture.` are runtime.

`&name`, `*name`, and `<<:` are part of the document. `yaml.safe_load` resolves them before a `Test` is built. The blueprint copies an aliased mapping when it builds a fixture or a test, so two tests do not share one sample dict. `$fixture.<name>` names a built fixture. `$r.<key>` names session data, including an `as` result. An anchor cannot do either, because those values do not exist at load time.

A management write preserves anchors. A `safe_dump` round-trip is not compliance: `safe_load` resolves anchors, and `safe_dump` does not emit them.

## Normative document

This is the document law, not a suggestion. `*plain` is the expected string. `$fixture.error_message` is the built instance. It is the law for a file that has all three roots. It is not a claim that proto's Python file already has all three.

```yaml
fixtures:
  error_message: &error_message
    module_path: &error_module tiferet.domain.error
    class_name: ErrorMessage
    attributes: &plain_message
      lang: &lang en_US
      text: &plain An error occurred.
  formatted_error_message:
    <<: *error_message
    attributes:
      lang: *lang
      text: &formatted 'An error occurred: {error}'

tests:
  error_message_format:
    conditions:
      fixtures: [error_message, formatted_error_message]
    execute:
      - target: error_message
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: *plain

testers:
  test_error:
    module_path: *error_module
    class_name: Error
    attributes:
      id: &error_id TEST_ERROR
      name: Test Error
      message: [$fixture.error_message]
    fixtures:
      error_message: *error_message
    tests:
      construction_derives_error_code:
        conditions:
          fixtures: [error_message]
        execute:
          - target: self
            method: new
            as: built
        assert:
          - outcome: built
            fields:
              id: *error_id
              error_code: *error_id
```

The snippet carries one anchor (`&error_message`), one alias (`*error_module`), one merge (`<<: *error_message`), one `$fixture.` reference (`$fixture.error_message`), and one `*alias` used as an expected value (`equals: *plain`).

## What stays absent

These stay absent. Do not restore them:

- `TesterService`
- `TesterConfigRepository`
- `TesterConfigObject`
- `TesterAggregate`
- `resolve_tester`
- tester events
- `Tester()`
- `test_case`

`testers:` is legal only as a root of a `tiferet_tests/**/*.yml` file. It is illegal in application `config.yml`. A `tiferet_tests/` file is not that forbidden section.

There is no AdminApp tester domain. A unit test is not dispatched through `AppSessionContext`. There is no stored callable, no `predicate` key, no `field_normalizers` key, and no YAML Python object tag.

## The Python grammar

The Python comment grammar is unchanged and stays beside the YAML roots. After preamble, a test module declares `# *** fixtures`, `# *** tests`, and `# *** testers`, in that order, and omits an empty group. Testers compose fixtures and tests; they do not replace them.

Under a tester class, members are `# * fixture:` and `# * test:`. `# * test:` is the only place a class member is a test rather than `# * method:`.

`@use_tester` (`tiferet.blueprints.tester`, exported from `tiferet`) injects `test_ctx` and `session` by parameter name and strips those names from the pytest signature. Types: `domain` | `aggregate` | `transfer_object` | `domain_event` | `service_event` | `generic` | `repo` | `context`.

```python
"""Tiferet Error Domain Tests"""

# *** imports

# ** app
from tiferet import use_tester
from tiferet.domain.error import ErrorMessage

# *** testers

# ** tester: test_error_message
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
    equality_fields=['lang', 'text'],
    description_cases=[('format', (), 'An error occurred.')],
)
class TestErrorMessage:
    '''
    Tests for ErrorMessage.
    '''

    # * test: new_and_format
    def test_new_and_format(self, test_ctx, session):
        '''
        Construct from sample data and assert description cases.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Assert construction and description methods.
        test_ctx.assert_new()
        test_ctx.assert_description()
```

Pytest is an optional extra (`pip install tiferet[test]`) and the runner for `tests/` (`testpaths = ["tests", "tests_int"]` in `pyproject.toml`). The `tiferet/` package does not import pytest. `tiferet/testing/` is absent. Do not recreate it. Pytest still collects `tests/**`. It does not collect YAML node ids.

## Module run

`run_test_module` (`tiferet/blueprints/tester.py`) is the module run. It is not a console script, not an admin command, and not exported from `tiferet`. It is not a second function. `summary=True` is the same run: it prints only the count line and returns the same outcomes.

The argument is the filesystem path of a Python test module. The entry reads `tests/<rel>.py` and `tiferet_tests/<rel>.yml`. It reads the Python path to prove the file exists and to derive `<rel>`. It does not import the Python module and does not call its tests. The YAML document is loaded through `YamlLoader.load` / `yaml.safe_load`. Extension is `.yml` only. A missing Python file raises `ValueError` before the YAML load. A missing YAML file raises the existing YAML not-found error. `conftest.py`, `__init__.py`, a path under `tests_int/`, a file not named `test_*.py`, a YAML path passed as the input, and a `variables:` root are refused before any test line.

Each root test, then each tester-contained test, gets one `TestContext` and one session. A tester is not a test and gets no `TestContext`. The entry builds the `Test` through the test config objects, compiles the three phases into `Feature.steps`, and binds the test with `TestContext.from_domain`. It injects a `get_dependency` that resolves the phase handlers the tester blueprint registered. It does not insert the test into a feature cache and does not call `AppSessionContext.run` or `build_app`.

`build_phase_runtime` stays on the tester blueprint. It builds a `PhaseRuntime` and binds `PhaseRuntimeContext` with `BaseContext.from_domain`. That callable is injected into the test context and wrapped by `TestContext.build_phase_runtime`. The context does not import the blueprint. `BaseContext.for_domain(PhaseRuntime)` is `PhaseRuntimeContext`. The bound model stays immutable. Built fixtures, arranged mocks, and `as` keys are context attributes. The runner does not import an aggregate.

The constructor switch is this handoff. `build_test_session` grows a keyword-only `test_context`. The module run calls `build_test_session(test_context=ctx)` and does not pass a `TesterContext`. On that construction `tester_ctx` is unset. `run` executes `test_context`. Pass means `execute_feature` returned. Fail means the run raised a `TiferetError`. A `ModelError` while the config objects build the `Test` also fails that test. The runner does not wrap one as the other. One failed test does not abort the module. The positional form `build_test_session(tester_ctx)` stays. `@use_tester` keeps calling it, and on that construction `test_context` is unset. Passing both collaborators, or neither, raises `ValueError`. `TestSessionContext` still omits `domain_type`.

The report uses YAML node ids. A root test is `tiferet_tests/<rel>.yml::<test_key>`. A contained test is `tiferet_tests/<rel>.yml::<tester_key>::<test_key>`. A passed line is `<nodeid> PASSED`. A failed line is `<nodeid> FAILED`, and the exception text follows before the next node id or the count. The count line is `N passed`, `N failed`, or `N failed, M passed`. No skipped. No banner. `0 passed` is the empty-document line.

A pytest plugin may call this entry with the Python module's filesystem path. It must not collect YAML instead of Python, must not skip a Python module because a counterpart exists, and must not hide a Python node id. This entry does not register a plugin, does not add a `pytest11` entry point, and does not import pytest. `testpaths` stays `["tests", "tests_int"]`.

A model defect is a `ModelError`. A failed run is a `TiferetError`. A failed check is an `AssertionError`. The runner records the error it caught. It does not turn one into the other.

## The writer

`tiferet.blueprints.tester` is the writer for one `tiferet_tests/<rel>.yml` document. The seventeen functions are `add_fixture`, `get_fixture`, `list_fixtures`, `update_fixture`, `remove_fixture`, `add_test`, `get_test`, `list_tests`, `update_test`, `remove_test`, `add_tester`, `get_tester`, `list_testers`, `update_tester`, `remove_tester`, `attach_test`, and `detach_test`. They forward to one delegation, `_delegate_test_module`. That function reads the bytes, calls `ReadTestModuleDocument`, calls the verb event, and, on a write, calls `WriteTestModuleDocument` and performs `os.replace`. Callers import the seventeen names from that module. They are not exported from `tiferet` or `tiferet.blueprints`. They are not a service, a repository, or admin commands.

The seventeen verbs are domain events in `tiferet/events/test_module.py`: `AddFixture`, `GetFixture`, `ListFixtures`, `UpdateFixture`, `RemoveFixture`, `AddTest`, `GetTest`, `ListTests`, `UpdateTest`, `RemoveTest`, `AddTester`, `GetTester`, `ListTesters`, `UpdateTester`, `RemoveTester`, `AttachTest`, and `DetachTest`. Each verifies that verb and calls an aggregate mutator. These are not tester events. They are not `TesterService`, not a repository, and not an event per blueprint name in a tester module.

`TestModuleDocument` (`tiferet/domain/test_module.py`) is the read-only document. `TestModuleAddress` is a field of that document. `text` is the loaded revision, or `None` when the file is absent. `body` is the composed root the read event attaches. `TestModuleDocumentAggregate` (`tiferet/mappers/test_module.py`) mutates the working graph. Its mutators are `add_entry`, `update_entry`, `remove_entry`, `attach`, `detach`, `assign_anchor`, `apply_merge`, and `omit_empty`. They are not the seventeen verb names. `AddFixture` and `AddTest` both call `add_entry`. The fixture event allows an alias and a merge. The test event refuses both.

YAML lookup and node surgery live in `tiferet/utils/yaml.py`. They do not know a fixture from a test and they do not raise a tester id. `TestModuleContext` binds the document and holds `working`. It does not decide an entry. It does not assign `domain.text` or `domain.body`. Address refusal stays on the context.

`rel` is the stem derived from `tests/<rel>.py` by dropping `.py`. The file is `base_dir/tiferet_tests/<rel>.yml`. The writer does not read the Python file and does not accept a filesystem path, so it cannot be pointed at application `config.yml`.

`attach_test` inserts the root test's node under `testers.<tester>.tests` under the same key. It does not copy the body and does not remove the root entry. `detach_test` drops that containment only. It does not remove the root test and does not clear the anchor name.

A management write records anchor names before the composer clears its table and emits those names, including a node referenced once. It goes through the anchored extension, not through `yaml.safe_dump`. A `safe_dump` round-trip is not compliance. The case payload stays an opaque mapping, or a YAML fragment when that mapping contains an anchor, an alias, or a merge. This writer does not name phase fields.

A `tiferet_tests/` file is still not an application `testers:` section. `TesterService` stays absent.

## Related Documentation

- [code_style.md](code_style.md) — artifact comments, including the test-module grammar
- [contexts.md](contexts.md) — `FeatureContext`, which `TestContext` extends
- [domain.md](domain.md) — `Feature`, which `Test` extends
