# Step 9: The Calculator as a Client

Every entry point so far has called the generic `App(...)` or `CLI(...)` and gotten back whatever context class the framework hands over. That's about to change: we're giving the calculator its **own** `AppSessionContext` subclass, so it can do one thing none of the built-in machinery does for us — remember every calculation it runs, without duplicating a "record it" step inside every single feature.

### 9.1 Why a custom context needs its own blueprint

It's tempting to assume that a session in `config.yml` declares a context type you can swap out. It doesn't: a session declares no context class at all, and `App(...)`'s composition chain builds a literal `AppSessionContext` — there's no dynamic class resolution on that path. (`CLI(...)` *looks* like it works this way, but it's actually its own dedicated, hardcoded composition chain, entirely separate from `App(...)`.)

So a custom `AppSessionContext` subclass needs its own blueprint. That's most of what this chapter builds.

### 9.2 From a per-feature step to a session-level concern

Back in Chapter 7, every arithmetic feature grew a second step — `record_calculation_event` — so its calculation would land in `history.json`. It worked, but look at the cost: six features, six copies of the same `service_id: record_calculation_event` block, each passing its own `operator` literal by hand. Add a seventh operator and you'd copy it a seventh time.

Recording history isn't really part of *what* `calc.add` computes — it's something we want to happen after *any* feature succeeds. That's a session-level concern, not a per-feature one, and `AppSessionContext` already has a natural seam for it: `execute_feature`.

**app/contexts/calc.py**

```python
class CalculatorAppContext(AppSessionContext):

    def __init__(self, ..., record_run_handler=None):
        super().__init__(...)
        self._record_run = record_run_handler

    def execute_feature(self, feature_id, request, **kwargs):
        super().execute_feature(feature_id, request, **kwargs)
        self.record_run(feature_id, request)

    def record_run(self, feature_id, request):
        if self._record_run is None:
            raise_unwired_handler_error('record_run_handler', self.domain.id, feature_id=feature_id)
        self._record_run(feature_id, request)
```

Because `AppSessionContext.run()` calls `execute_feature` inside a `try/except TiferetError` block, `record_run` only fires *after* a successful run — an exception from `super().execute_feature(...)` propagates straight past it, so a failed division never pollutes the history. That single override replaces six hand-duplicated steps.

Now `record_calculation_event` can go — the arithmetic features in `config.yml` shrink back to one step each:

```yaml
add:
  name: Add Number
  steps:
    - service_id: add_number_event
      name: Add `a` and `b`
```

Delete the `record_calculation_event` service registration too; nothing declares it anymore.

### 9.3 Deriving the operator instead of passing it in

The old `record_calculation_event` step received its `operator` as a literal parameter (`params: {operator: '+'}`). Since `record_run` fires generically after *any* feature — arithmetic or not — `RecordCalculation` needs to figure out the operator itself, or gracefully do nothing when there isn't one:

**app/events/history.py**

```python
class RecordCalculation(DomainEvent):

    def execute(self, feature_id, a=None, b=None, result=None, history_file='history.json', max_entries=10, **kwargs):
        if result is None:
            return result

        operator = FEATURE_OPERATOR_MAP.get(feature_id)
        if operator is None:
            return result   # formula.*, calc.history, etc. -- nothing to record

        expression = f'{operator}{a}' if b is None else f'{a} {operator} {b}'
        # ... read, append, trim, persist -- unchanged from Chapter 7
```

`FEATURE_OPERATOR_MAP` (`calc.add` → `+`, `calc.subtract` → `-`, …) lives in `app/assets/core.py` — we'll build the rest of that module in Chapter 10.

### 9.4 Wiring record_run into the blueprint

`record_run_handler` is a factory, shaped just like the framework's own `execute_feature_handler`/`raise_error_handler`: it closes over `get_dependency` and returns the actual handler function.

**app/blueprints/calc.py**

```python
def record_run_handler(get_dependency):
    def handler(feature_id, request):
        # request.result carries the feature's final response; request.data
        # still carries the raw a/b operands the arithmetic step read.
        record_run_evt = get_dependency('record_run_event', 'app')
        record_run_evt.execute(feature_id=feature_id, result=request.result, **request.data)
    return handler

def build_calculator_app_context(app_session, cache):
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)
    return CalculatorAppContext.from_domain(
        app_session,
        get_dependency=resolver.get_dependency,
        cache=cache,
        build_logger_handler=core.build_logger_handler(cache, resolver.get_dependency),
        execute_feature_handler=core.execute_feature_handler(resolver.get_dependency, cache),
        raise_error_handler=core.raise_error_handler(core.get_error(cache, resolver.get_dependency)),
        response_handler=core.response_handler,
        create_request_handler=core.create_session_request,
        record_run_handler=record_run_handler(resolver.get_dependency),
    )

def create_calculator_app(interface_id='calc_client', config_file='config.yml'):
    cache = core.build_cache()
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)
    return build_calculator_app_context(app_session, cache)
```

Register `record_run_event` under the session's own `services:` block in `config.yml`, alongside a rename that sets up a naming scheme we'll lean on for the rest of the tutorial:

```yaml
sessions:
  calc_client:
    name: Calculator Client
    services:
      record_run_event:
        module_path: app.events.history
        class_name: RecordCalculation
```

`CalculatorAppContext` is wired explicitly by `create_calculator_app`, never resolved from config. Rename `basic_calc.py` to `calc_client.py` and swap its one line:

```python
from app.blueprints.calc import create_calculator_app

app = create_calculator_app(interface_id='calc_client')
```

### 9.5 See it work

```bash
python calc_client.py
```

Same arithmetic output as Chapter 5, plus history that no longer needed a second step in every feature to produce:

```
1 + 2 = 3.0
5 - 3 = 2.0
4 * 3 = 12.0
8 / 2 = 4.0
Error: Cannot divide by zero
2 ** 3 = 8
√16 = 4.0

Recent calculations:
1.0 + 2.0 = 3.0
5.0 - 3.0 = 2.0
4.0 * 3.0 = 12.0
8.0 / 2.0 = 4.0
2 ** 3 = 8
√16 = 4.0
```

### 9.6 Recap

`CalculatorAppContext` now owns one session-level concern — `record_run` — instead of every arithmetic feature owning a copy of it. Next, we'll give the arithmetic operators themselves the same treatment: instead of living in `config.yml`, they become defaults the calculator ships with, regardless of configuration.

→ Head to **[Step 10: The Arithmetic Operators as a Bounded Context](10-the-arithmetic-operators-as-a-bounded-context.md)**
