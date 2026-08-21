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
    CALC_ADD_ID: CALC_ADD_DATA,
    CALC_SUBTRACT_ID: CALC_SUBTRACT_DATA,
    # ...
}
```

No `flags` here -- that gets injected on the way into the cache, in a moment. **app/assets/error.py** does the same for `INVALID_INPUT` and `DIVISION_BY_ZERO`, via `create_default_error_data`, since both are raised directly by the arithmetic events and belong to the bounded context, not to a consumer's `config.yml`.

### 10.2 Seeding the defaults via a calculator-local cache builder

Tiferet's own core defaults are seeded onto the bootstrap cache by `tiferet.blueprints.core.build_cache`, using three stacked decorators: `@add_default_errors`, `@add_default_features`, `@add_default_app_services`. We reuse that same stacked-decorator shape, but scoped to the calculator's own bounded context with its own decorators -- `add_default_calc_features`/`add_default_calc_services` (`app/contexts/calc.py`), not the framework's `'app'`-scoped ones:

**app/blueprints/calc.py**

```python
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_calc_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_calc_services(a.core.CALC_DEFAULT_SERVICES)
def build_calculator_cache(cache=None):
    return core.build_cache(cache)
```

`create_calculator_app` now calls `build_calculator_cache()` instead of `core.build_cache()`. Since `calc.add` and friends are no longer declared in `config.yml` at all, a successful run already proves the default-catalog resolution path works end to end.

### 10.3 Giving the calculator its own DI namespace

Here's a subtlety worth understanding, not just copying: the ordinary per-flag feature DI system that resolves a feature step's `service_id` reads registrations **exclusively** from `config.yml`'s `services:` block, with no cache fallback. Left alone, a cache-seeded default feature would have no way to resolve its own step's service -- it needs *some* pre-built container to resolve against.

An earlier version of this design routed that resolution through the framework's own `'app'`-flagged container -- the same one holding the framework's core defaults -- by seeding `CALC_DEFAULT_SERVICES` into that shared namespace and tagging every feature `flags=['app']`. It worked, but the calculator's own services became indistinguishable from the framework's in the cache. The calculator deserves its own namespace, and giving it one is a small, one-time cameo appearance of Tiferet's `di` layer -- the only place in this entire tutorial that touches it directly, and it needs nothing new from that layer, only two pieces the framework already ships:

**app/contexts/calc.py**

```python
CALC_SERVICE_CACHE_PREFIX = ('calc', 'services')

def add_default_calc_services(services):
    # Same shape as tiferet's own add_default_app_services, seeding
    # AppServiceDependency entries under CALC_SERVICE_CACHE_PREFIX instead.
    ...

def get_default_calc_services(cache):
    return list(cache.get_by_prefix(*CALC_SERVICE_CACHE_PREFIX).values())

def add_default_calc_features(features):
    # Auto-tags every feature flags=['calc'] on the way into the cache, via
    # tiferet's own add_default_features -- callers never write the flag by hand.
    return add_default_features({
        feature_id: {**feature_data, 'flags': ['calc']}
        for feature_id, feature_data in features.items()
    })
```

**app/blueprints/calc.py**

```python
from tiferet.di import DIDynamicServiceContainer

def build_calc_service_container(cache):
    services_by_id = {s.service_id: s for s in get_default_calc_services(cache)}
    return DIDynamicServiceContainer(services=services_by_id)

def register_calc_container(resolver, cache):
    resolver.add_container(build_calc_service_container(cache), 'calc')
```

`register_calc_container` is called once, right after `build_service_resolver`, everywhere a calculator session is composed. Notice it's a plain `DIDynamicServiceContainer` (Factory-scoped -- a new instance per resolution), not a `DIAppServiceContainer` (Singleton-scoped, meant for shared infrastructure like loggers, repos, or the resolver itself). The arithmetic events are ordinary feature-step services that happen to ship as defaults, not app-level infrastructure, so a `calc`-flagged default now resolves *exactly* the way a `config.yml`-declared feature service would -- same container type, same scope -- the only difference is where it's registered from.

### 10.4 Giving the CLI the same defaults

`App(...)` and `CLI(...)` never see `build_calculator_cache()` -- they build the framework's own cache. Since `calc_cli.py` still used the generic `CLI(...)` up to this point, it would lose the arithmetic operators the moment `config.yml` stopped declaring them. It needs the same treatment as `create_calculator_app`, stacked on top of the CLI blueprint's own cache builder instead of the core one -- and, since `tiferet.blueprints.cli.build_cli_session_context` builds and consumes its own resolver internally with no hook to register an extra container, the CLI path needs a calculator-local mirror of it too, with one line added:

**app/blueprints/calc.py**

```python
@add_default_errors(a.error.CALC_DEFAULT_ERRORS)
@add_default_calc_features(a.feature.CALC_DEFAULT_FEATURES)
@add_default_calc_services(a.core.CALC_DEFAULT_SERVICES)
def build_calculator_cli_cache(cache=None):
    return cli_bp.build_cli_cache(cache)

def build_calculator_cli_session_context(app_session, cache):
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)
    register_calc_container(resolver, cache)   # the one addition over cli_bp's own builder
    # ... the rest mirrors tiferet.blueprints.cli.build_cli_session_context exactly

def create_calculator_cli(interface_id='calc_cli', argv=None, config_file='config.yml'):
    cache = build_calculator_cli_cache()
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)
    cli_context = build_calculator_cli_session_context(app_session, cache)
    return cli_context.run(argv)
```

`CliContext` has no `record_run` override, so CLI runs get the arithmetic defaults but not history recording -- a small, accepted scope boundary; `calc_client.py` and `calc_fluent.py` (Chapter 11) are where history matters.

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

The arithmetic operators are now a genuine bounded context: default behavior the calculator ships with at the interface level, built from the same `create_default_feature_data`/`create_app_service_dependency_data` factories the framework uses for its own defaults, and resolved through the calculator's own dedicated `'calc'`-flagged container -- not borrowed from the framework's `'app'` namespace. `formula.*` and `calc.history` stay hand-declared in `config.yml`, since they're consumer-configurable behavior rather than the bounded context's fixed interface contract.

Everything is now in place for the closing chapter: a fluent, chainable client built on top of this same bounded context.

→ Head to **[Step 11: The Fluent Calculator Context](11-the-fluent-calculator-context.md)**
