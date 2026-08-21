# Step 11: The Fluent Calculator Context

Everything in Chapters 9-10 was in service of this closing chapter: a chainable, `PEMDAS`-aware calculator client built on top of the bounded context.

```python
calc_app = create_calculator_fluent()
result = calc_app.add(1, 3).subtract_from(5).multiply_by(2).run()   # -6.0
```

### 11.1 Splitting the client from the fluent surface

`CalculatorAppContext` (Chapter 9) is the plain client: `run()`, plus `record_run`. The fluent surface — `add`/`add_to`, `.pending`, `.reset()`, and (as we'll get to) `run()` itself — is a distinct set of concerns layered on top, so it gets its own subclass rather than growing `CalculatorAppContext` indefinitely:

**app/contexts/fluent.py**

```python
class CalculatorFluentContext(CalculatorAppContext):
    ...
```

And its own blueprint, mirroring `build_calculator_app_context`/`create_calculator_app` exactly, just realizing `CalculatorFluentContext` instead:

**app/blueprints/fluent.py**

```python
def build_calculator_fluent_context(app_session, cache):
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)
    return CalculatorFluentContext.from_domain(
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

def create_calculator_fluent(interface_id='calc_fluent', config_file='config.yml'):
    cache = build_calculator_cache()
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)
    return build_calculator_fluent_context(app_session, cache)
```

`calc_fluent.py` becomes one line: `calc_app = create_calculator_fluent()`. Update the `calc_fluent` session's (informational) `class_name` in `config.yml` to `CalculatorFluentContext`, `module_path` to `app.contexts.fluent`.

### 11.2 A persistent request *is* the chain

A fluent chain isn't several requests that need correlating — it's **one** request with many steps. `Request`/`RequestContext` already carry a `session_id`, auto-generated per call — so instead of inventing a parallel "expression id" and a cache-backed side object to hold pending state, we hold one `FluentRequestContext` in memory for the whole chain and let its own `session_id` uniquely identify it, for free.

**app/contexts/fluent.py**

```python
class FluentRequestContext(RequestContext):
    """A request specialized for one entry point, mirroring CliRequestContext."""

    def start(self, value):
        self.data['values'] = [float(value)]
        self.data['operators'] = []

    def log_term(self, operator, operand):
        self.data.setdefault('operators', []).append(operator)
        self.data.setdefault('values', []).append(float(operand))

    @property
    def terms(self):
        return list(self.data.get('values', [])), list(self.data.get('operators', []))
```

Every operator gets two methods, exactly as before — a **starter** (two operands, begins a new expression: `add(a, b)`) and a **continuation** (one operand, folds into the active one: `add_to(x)`). Both just log a term; neither computes anything yet:

```python
class CalculatorFluentContext(CalculatorAppContext):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_request = None

    def _start(self, operator, first, second):
        self._guard(self._pending_request is None, EXPRESSION_ALREADY_ACTIVE_ID)
        self._pending_request = FluentRequestContext()
        self._pending_request.start(first)
        self._pending_request.log_term(operator, second)
        return self

    def _continue(self, operator, operand):
        self._guard(self._pending_request is not None, NO_ACTIVE_EXPRESSION_ID)
        self._pending_request.log_term(operator, operand)
        return self

    def add(self, a, b):
        return self._start(ADD_OPERATOR, a, b)

    def add_to(self, x):
        return self._continue(ADD_OPERATOR, x)
```

No `self.run(...)` happens here — not for `.add()`, not for `.multiply_by()`. Every intermediate call is nothing more than a list append; nothing is dispatched, logged to a logger, or recorded until the chain finalizes.

### 11.3 Resolving PEMDAS on the `Expression` domain object

The old design reduced eagerly, one pairwise operation at a time, as each term arrived — a real "shunting yard" (the standard technique for precedence-aware parsing: hold pending values/operators on two stacks, and only reduce the top once you know nothing higher-precedence is coming to claim it first) running incrementally across the whole chain. Since nothing is dispatched until the chain finalizes now, there's no reason to reduce incrementally either: the entire scheduling pass can happen once, at the very end, over the complete, already-logged term list. That's exactly the kind of self-contained algorithm a domain object should own:

**app/domain/expression.py**

```python
class Expression(DomainObject):
    values: List[float] = Field(default_factory=list)
    operators: List[str] = Field(default_factory=list)

    def resolve(self, reduce):
        pending_values = [self.values[0]]
        pending_operators = []

        for operator, operand in zip(self.operators, self.values[1:]):
            while pending_operators and OPERATOR_PRECEDENCE[pending_operators[-1]] >= OPERATOR_PRECEDENCE[operator]:
                top_operator = pending_operators.pop()
                right = pending_values.pop()
                left = pending_values.pop()
                pending_values.append(reduce(top_operator, left, right))
            pending_operators.append(operator)
            pending_values.append(operand)

        while pending_operators:
            top_operator = pending_operators.pop()
            right = pending_values.pop()
            left = pending_values.pop()
            pending_values.append(reduce(top_operator, left, right))

        return pending_values[0]
```

This is the same shunting-yard algorithm from before, just run once over the whole list instead of interleaved with logging. `reduce` is still just a callable `Expression` is handed — it has no idea what actually computes `left op right`. That's deliberately kept one layer up, so this domain object stays a pure scheduling algorithm with zero framework or DI knowledge. The old cache-backed `ExpressionContext` — with its `load`/`save`/discard round-trip — is retired entirely; there's nothing left to key by id and look up later, since the accumulating state is held directly rather than serialized out to a shared cache.

### 11.4 Collapsing the whole chain into one `calc.resolve` run -- by overriding `run()` itself

Here's the payoff, and it's a little more interesting than just wiring: `CalculatorFluentContext` overrides `run()` itself, so finishing a chain reads exactly like running any other feature: `calc_app.add(1, 3).subtract_from(5).multiply_by(2).run()`.

That only works because `run()` isn't really about `feature_id` the way it looks. `feature_id` is a first-class requirement of `execute_feature`'s single-feature dispatch -- but `run()` itself is a fundamentally agnostic executor; it only *looks* like `feature_id` is mandatory because the base workflow needs one to build a request and resolve a step. Once a chain is active, there's already exactly one thing left to run, so that requirement can be relaxed for this one case, as long as the relaxation is explicit:

```python
def build_request(self, feature_id, headers={}, data={}):
    if self._pending_request is not None:
        self._pending_request.feature_id = feature_id
        return self._pending_request
    return super().build_request(feature_id, headers, data)

def run(self, feature_id=None, headers={}, data={}, **kwargs):
    # No chain active: defer entirely to the plain client's run().
    if self._pending_request is None:
        return super().run(feature_id, headers, data, **kwargs)

    # A chain is active: resolve it into a single value.
    value = super().run('calc.resolve', data={})
    self._pending_request = None
    return value
```

Two cases, one method:

- **No chain active** — every argument, `feature_id` included, passes straight through to the plain client unchanged. This is what lets a configured feature keep working exactly as before: `calc_app.run('calc.history', data={})` still runs `calc.history`, because at that point `self._pending_request` is `None`. If you forget `feature_id` here, there's no special guard for it — the framework's own feature lookup raises `FEATURE_NOT_FOUND` on its own, which is exactly the safeguard we want; `run()` doesn't need to reinvent it.
- **A chain is active** — every argument is irrelevant, `feature_id` included. There's only one thing left to do, so `run()` does it: a single `super().run('calc.resolve', ...)` call (note the `super()` — calling `self.run(...)` here would just re-enter this same override and recurse). Passing an explicit `feature_id` while a chain happens to be active is simply ignored rather than specially guarded against; resolving the active chain is the only sensible thing left to do either way.

`super().run('calc.resolve', ...)` is the *only* `run()` call the entire chain ever makes — one logger build, one `execute_feature`, and (via the `record_run` machinery from Chapter 9) exactly one history entry recording the whole expression, instead of one entry per pairwise reduction.

`calc.resolve` is a single-step bounded-context default feature, registered the same way as `calc.add` and friends in Chapter 10. Its step's event, `ResolveExpression`, receives the logged `values`/`operators` straight from `request.data` and does the actual reduction — dispatching each pairwise operation through the calculator's own arithmetic events (constructor-injected as siblings from the same bounded-context service container), so validation and division-by-zero handling are reused completely unchanged:

**app/events/expression.py**

```python
class ResolveExpression(DomainEvent):

    def __init__(self, add_number_event, subtract_number_event, multiply_number_event, divide_number_event):
        self._operator_events = {
            ADD_OPERATOR: add_number_event,
            SUBTRACT_OPERATOR: subtract_number_event,
            MULTIPLY_OPERATOR: multiply_number_event,
            DIVIDE_OPERATOR: divide_number_event,
        }

    def execute(self, values, operators, **kwargs):
        expression = Expression(values=values, operators=operators)
        return expression.resolve(reduce=self.execute_operator)

    def execute_operator(self, operator, left, right):
        return self._operator_events[operator].execute(a=left, b=right)
```

Because `add_number_event`, `subtract_number_event`, `multiply_number_event`, and `divide_number_event` are already registered by `CALC_DEFAULT_SERVICES` (Chapter 10) under exactly those ids, Tiferet's DI container wires them in as sibling providers automatically — `ResolveExpression` never has to look anything up itself beyond its own `_operator_events` map.

Finally, `RecordCalculation` (Chapter 9) needs to recognize this shape of run: a `calc.resolve` call carries `values`/`operators` in `request.data` instead of a single `a`/`b` pair, so it renders the whole logged expression via `Expression.display()` rather than deriving one from `feature_id`:

```python
def execute(self, feature_id, a=None, b=None, values=None, operators=None, result=None, ...):
    if result is None:
        return result
    if values is not None and operators is not None:
        expression = Expression(values=values, operators=operators).display()
    else:
        operator = FEATURE_OPERATOR_MAP.get(feature_id)
        if operator is None:
            return result
        expression = f'{operator}{a}' if b is None else f'{a} {operator} {b}'
    # ... read, append, trim, persist -- unchanged
```

`subtract`/`multiply`/`divide` and their `_from`/`_by` continuations, plus `.reset()` and `.pending`, follow the exact same patterns — see `app/contexts/fluent.py` for the full set.

### 11.5 See it work

**calc_fluent.py**

```python
from app.blueprints.fluent import create_calculator_fluent
from tiferet import TiferetError

calc_app = create_calculator_fluent()

try:
    result = calc_app.add(1, 3).subtract_from(5).multiply_by(2).run()
    print(f'1 + 3 - 5 * 2 = {result}')
except TiferetError as e:
    print(f'Error: {e.message}')

result = calc_app.add(2, 3).multiply_by(4).subtract_from(1).run()
print(f'2 + 3 * 4 - 1 = {result}')

result = calc_app.multiply(3, 4).add_to(5).divide_by(2).run()
print(f'3 * 4 + 5 / 2 = {result}')

print('\nRecent calculations:')
print(calc_app.run('calc.history', data={}))
```

```bash
python calc_fluent.py
```

```
1 + 3 - 5 * 2 = -6.0
2 + 3 * 4 - 1 = 13.0
3 * 4 + 5 / 2 = 14.5

Recent calculations:
1.0 + 3.0 - 5.0 * 2.0 = -6.0
2.0 + 3.0 * 4.0 - 1.0 = 13.0
3.0 * 4.0 + 5.0 / 2.0 = 14.5
```

Notice the history now shows one line **per chain**, not one per pairwise reduction as it would have with the old eager design — a direct, visible consequence of collapsing every chain into a single `calc.resolve` run.

Walk through the first chain by hand: `add(1, 3)` and `.subtract_from(5)` and `.multiply_by(2)` only ever append to the logged term list — `values=[1, 3, 5, 2]`, `operators=['+', '-', '*']`. Nothing is computed until `.run()` calls `super().run('calc.resolve', ...)`, which hands that exact list to `Expression.resolve`. It walks the list once: `'+'` then `'-'` (same precedence, so `1 + 3 = 4` reduces immediately once `'-'` arrives), then `'*'` arrives with *higher* precedence than the pending `'-'`, so it's pushed without reducing. Draining what's left afterward — lowest precedence last — gives `5 * 2 = 10`, then `4 - 10 = -6`.

### 11.6 Recap

Across eleven chapters you've now touched every layer Tiferet has: **domain** objects (`Formula`, `Expression`), **mappers** (`FormulaAggregate`/`FormulaConfigObject`), **interfaces** (`FormulaService`), **repos** (`FormulaConfigRepository`), **events** (arithmetic, history, formula, and `ResolveExpression`), **assets** (the calculator's own bounded-context defaults), **contexts** (`CalculatorAppContext`, `CalculatorFluentContext`), **blueprints** (`create_calculator_app`, `create_calculator_cli`, `create_calculator_fluent`), and, in one deliberate cameo (Chapter 10), **di** (`DIDynamicServiceContainer`, registered under the calculator's own `'calc'` flag via `register_calc_container`) — all wired together through one consolidated `config.yml`. That `di` appearance is the only one of its kind in the tutorial, and it required authoring nothing new in that layer: everywhere else, DI wiring happens through the higher-level `add_default_*`/`build_service_resolver` blueprint functions, never a raw container type directly.

The fluent context didn't require reinventing any arithmetic: it added a small scheduling layer on top of features you'd already built, and reused the framework's own request as the one thing a multi-call chain actually is — a single request with many steps — instead of inventing a parallel correlation mechanism. That's really the whole idea behind Tiferet's layering — each new capability should mostly be *composition*, not more special cases.

From here, natural next steps: exponentiation in the chain (right-associative, so the reduction rule needs a small tweak), a `.pending` tour through the logged terms for a "show your work" mode, or swapping the in-memory chain for something that survives process restarts.

You built a calculator that does long division on the order of operations. Nicely done.

→ Back to the **[tutorial index](index.md)**.
