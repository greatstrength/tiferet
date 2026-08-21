# Step 10: The Arithmetic Operators as a Bounded Context

`calc.add`, `calc.subtract`, `calc.multiply`, `calc.divide`, `calc.exp`, and `calc.sqrt` have lived in `config.yml` since Chapter 4. That's fine for consumer-configurable behavior — but the arithmetic operators aren't really configuration. They're the calculator's own fixed, built-in vocabulary: no one integrating with this calculator should be able to accidentally delete `calc.add` from a YAML file and break addition. In DDD terms, they're a **bounded context** the calculator itself owns, and it should ship with default behavior at the interface level regardless of what `config.yml` says.

### 10.1 The assets layer: naming the operators once

Assets are Tiferet's root layer — pure constants, no framework imports. `app/assets/core.py` captures every id the bounded context needs, once, so nothing downstream restates a literal string like `'calc.add'` a second time.

**app/assets/core.py** (the shape of it)

```python
ADD_OPERATOR = '+'
SUBTRACT_OPERATOR = '-'
MULTIPLY_OPERATOR = '*'
DIVIDE_OPERATOR = '/'

CALC_ADD_ID = 'calc.add'
CALC_SUBTRACT_ID = 'calc.subtract'
# ... one *_ID per feature

OPERATOR_PRECEDENCE = {ADD_OPERATOR: 1, SUBTRACT_OPERATOR: 1, MULTIPLY_OPERATOR: 2, DIVIDE_OPERATOR: 2}
OPERATOR_FEATURE_MAP = {ADD_OPERATOR: CALC_ADD_ID, ...}          # operator -> feature id
FEATURE_OPERATOR_MAP = {CALC_ADD_ID: ADD_OPERATOR, ...}          # feature id -> operator (used by RecordCalculation, Chapter 9)

ADD_NUMBER_EVT_ID = 'add_number_event'
# ... one *_EVT_ID per arithmetic event

ADD_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path('app', TIFERET_EVENTS_PATH, 'calc'),
    'AddNumber',
)
# ... one *_EVT_DATA per arithmetic event, built the same way

CALC_DEFAULT_SERVICES = {
    ADD_NUMBER_EVT_ID: ADD_NUMBER_EVT_DATA,
    SUBTRACT_NUMBER_EVT_ID: SUBTRACT_NUMBER_EVT_DATA,
    # ...
}
```

`create_app_service_dependency_data`/`create_service_module_path` are the same factory helpers `tiferet.assets.core` uses to build its *own* default catalogs — we're reusing the framework's own pattern for the calculator's bounded context, not inventing a new one.

**app/assets/feature.py** builds one `create_default_feature_data(...)` entry per operator, keyed by the ids from `core.py`:

```python
CALC_ADD_DATA = create_default_feature_data(
    name='Add Number',
    group_id='calc',
    feature_key='add',
    steps=[{'service_id': ADD_NUMBER_EVT_ID, 'name': 'Add `a` and `b`'}],
    params_schema=create_params_schema(a='float', b='float'),
)

CALC_DEFAULT_FEATURES = {
    feature_id: {**feature_data, 'flags': ['app']}
    for feature_id, feature_data in {
        CALC_ADD_ID: CALC_ADD_DATA,
        CALC_SUBTRACT_ID: CALC_SUBTRACT_DATA,
        # ...
    }.items()
}
```

We'll come back to that `flags=['app']` in a moment — it's not optional. **app/assets/error.py** does the same for `INVALID_INPUT` and `DIVISION_BY_ZERO`, via `create_default_error_data`, since both are raised directly by the arithmetic events and belong to the bounded context, not to a consumer's `config.yml`.

### 10.2 Seeding the defaults via a calculator-local cache builder

Tiferet's own core defaults are seeded onto the bootstrap cache by `tiferet.blueprints.core.build_cache`, using three stacked decorators: `@add_default_errors`, `@add_default_features`, `@add_default_app_services`. We reuse exactly that pattern, scoped to the calculator's own bounded context instead of the framework core:

**app/blueprints/calc.py**

```python
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_app_services(a.core.CALC_DEFAULT_SERVICES)
def build_calculator_cache(cache=None):
    return core.build_cache(cache)
```

`create_calculator_app` now calls `build_calculator_cache()` instead of `core.build_cache()`. Since `calc.add` and friends are no longer declared in `config.yml` at all, a successful run already proves the default-catalog resolution path works end to end.

### 10.3 Why default features need `flags=['app']`

Here's a subtlety worth understanding, not just copying: `add_default_app_services` only seeds the **app-level** singleton container — the one framework plumbing resolves via an explicit `'app'` flag. The ordinary per-flag feature DI system that resolves a feature step's `service_id` reads registrations **exclusively** from `config.yml`'s `services:` block, with no cache fallback. Left alone, a cache-seeded default feature would have no way to resolve its own step's service.

Tagging every default feature `flags=['app']` routes its step resolution through that same `'app'`-flagged container instead — the one place `CALC_DEFAULT_SERVICES` actually lives. It's a real, if slightly surprising, seam in how the two DI systems relate; once you've seen it, `flags=['app']` on a cache-seeded feature makes sense as "this feature's service lives where the app-level defaults live," not as an arbitrary tag.

### 10.4 Giving the CLI the same defaults

`App(...)` and `CLI(...)` never see `build_calculator_cache()` — they build the framework's own cache. Since `calc_cli.py` still used the generic `CLI(...)` up to this point, it would lose the arithmetic operators the moment `config.yml` stopped declaring them. It needs the same treatment as `create_calculator_app`, stacked on top of the CLI blueprint's own cache builder instead of the core one:

**app/blueprints/calc.py**

```python
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_app_services(a.core.CALC_DEFAULT_SERVICES)
def build_calculator_cli_cache(cache=None):
    return cli_bp.build_cli_cache(cache)

def create_calculator_cli(interface_id='calc_cli', argv=None, config_file='config.yml'):
    cache = build_calculator_cli_cache()
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)
    cli_context = cli_bp.build_cli_session_context(app_session, cache)
    return cli_context.run(argv)
```

`CliContext` has no `record_run` override, so CLI runs get the arithmetic defaults but not history recording — a small, accepted scope boundary; `calc_client.py` and `calc_fluent.py` (Chapter 11) are where history matters.

**calc_cli.py** shrinks to one call:

```python
from app.blueprints.calc import create_calculator_cli

if __name__ == '__main__':
    create_calculator_cli()
```

### 10.5 config.yml shrinks

Delete the `calc.add`/`subtract`/`multiply`/`divide`/`exp`/`sqrt` feature declarations and their `*_number_event` service registrations entirely — they're calculator-local defaults now, present regardless of configuration. `calc.safe_divide` stays; it has no CLI command and exists solely to demonstrate the `condition:` step field, so it stays a config-authoring example rather than folding into the default catalog.

### 10.6 See it work

```bash
python calc_client.py
python calc_cli.py calc add 19 23
```

Both still produce exactly the output from Chapters 5 and 6 — but `config.yml` no longer declares a single arithmetic feature.

### 10.7 Recap

The arithmetic operators are now a genuine bounded context: default behavior the calculator ships with at the interface level, built from the same `create_default_feature_data`/`create_app_service_dependency_data` factories the framework uses for its own defaults, and resolved through the app-level container via `flags=['app']`. `formula.*` and `calc.history` stay hand-declared in `config.yml`, since they're consumer-configurable behavior rather than the bounded context's fixed interface contract.

Everything is now in place for the closing chapter: a fluent, chainable client built on top of this same bounded context.

→ Head to **[Step 11: The Fluent Calculator Context](11-the-fluent-calculator-context.md)**
