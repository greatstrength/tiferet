# Step 9: The Fluent Calculator Context

We've built arithmetic events, a validation utility, config-driven features, a CLI, persisted history, and a full formula domain model. That's domain, mappers, interfaces, repos, and events — five of Tiferet's layers, all exercised. This closing chapter reaches for the last three: **assets**, **contexts**, and **blueprints** — by building a chainable, `PEMDAS`-aware calculator client:

```python
calc_app = create_calculator_app()
result = calc_app.add(1, 3).subtract_from(5).multiply_by(2).result   # -6
```

### 9.1 Why this needs a new blueprint

Every other entry point in this app has used `App(...)` or `CLI(...)` and gotten back whatever context class the framework hands over. It's tempting to assume that pointing an interface's `module_path`/`class_name` at a custom class in `config.yml` is enough to swap in your own. It isn't, today: `App(...)`'s composition chain builds a literal `AppSessionContext` — there's no dynamic class resolution on that path. (The CLI entry point *looks* like it works this way, but it's actually its own dedicated, hardcoded composition chain, entirely separate from `App(...)`.)

So a custom, fluent `AppSessionContext` subclass needs its own blueprint, mirroring how the CLI's is built. That's most of what this chapter does.

### 9.2 The assets layer: naming the operators

Assets are Tiferet's root layer — pure constants, no framework imports. We've been leaning on `config.yml` for configuration data everywhere else, but the mapping from an operator *symbol* to its *precedence* and the *feature* that implements it is really compile-time knowledge our code depends on, not something an operator should read from a file. That's exactly what assets are for.

**app/assets/calc.py**

```python
ADD_OPERATOR = '+'
SUBTRACT_OPERATOR = '-'
MULTIPLY_OPERATOR = '*'
DIVIDE_OPERATOR = '/'

OPERATOR_PRECEDENCE = {
    ADD_OPERATOR: 1, SUBTRACT_OPERATOR: 1,
    MULTIPLY_OPERATOR: 2, DIVIDE_OPERATOR: 2,
}

OPERATOR_FEATURE_MAP = {
    ADD_OPERATOR: 'calc.add', SUBTRACT_OPERATOR: 'calc.subtract',
    MULTIPLY_OPERATOR: 'calc.multiply', DIVIDE_OPERATOR: 'calc.divide',
}

CALC_EXPRESSION_CACHE_PREFIX = ('calc', 'expressions')

NO_ACTIVE_EXPRESSION_ID = 'NO_ACTIVE_EXPRESSION'
EXPRESSION_ALREADY_ACTIVE_ID = 'EXPRESSION_ALREADY_ACTIVE'
```

`OPERATOR_FEATURE_MAP` is the key idea: it formally documents which of the arithmetic features you already built backs each operator. Nothing about arithmetic gets reinvented here — we're going to reuse `calc.add`/`calc.subtract`/`calc.multiply`/`calc.divide` exactly as they're already configured, validation, division-by-zero checks, history recording, and all.

### 9.3 The Expression domain model

A fluent chain needs somewhere to keep its pending state *between* calls — you might call `.add(1, 3)` and `.multiply_by(2)` as two entirely separate Python statements. That pending state is a small, cache-scoped runtime object, not something ever persisted to a config file. There's already a precedent for this in the framework: `Request` is a plain `DomainObject`, and `RequestContext` mutates it directly — no Aggregate in between. We follow the same pattern.

**app/domain/expression.py**

```python
class ExpressionState(DomainObject):
    """A snapshot of the pending stacks, captured after every operation."""
    label: str
    values: List[float] = []
    operators: List[str] = []

class Expression(DomainObject):
    """An in-progress expression, built one fluent call at a time."""
    id: str
    values: List[float] = []
    operators: List[str] = []
    history: List[ExpressionState] = []

    def display(self) -> str:
        """Render the pending expression as an infix string, e.g. '4 - 5 * 2'."""
        ...
```

`history` is what lets us explain *how* a result was reached later — every operation appends a snapshot before it's forgotten.

### 9.4 ExpressionContext: the calculator's own request context

Every feature execution gets a `RequestContext` wrapping a `Request` for that single call. A fluent chain is the same idea, one level up: it's an in-flight unit of work that spans *multiple* calls. `ExpressionContext` plays that role for the chain as a whole — load it, mutate it, save it back to the cache.

The interesting part is the algorithm. Operations arrive one at a time, but PEMDAS requires higher-precedence operators to bind *before* lower-precedence ones, even when they arrive later in the chain. The standard technique for this is operator-precedence parsing (a "shunting yard"): keep two stacks, and only reduce the top of the stack once you know nothing higher-precedence is coming to claim it first.

**app/contexts/expression.py** (the core of it)

```python
class ExpressionContext(BaseContext):
    domain_type = Expression

    def apply_term(self, operator, operand, reduce):
        # Reduce anything pending that binds at least as tightly as the incoming operator.
        while self.domain.operators and OPERATOR_PRECEDENCE[self.domain.operators[-1]] >= OPERATOR_PRECEDENCE[operator]:
            top_operator = self.domain.operators.pop()
            right = self.domain.values.pop()
            left = self.domain.values.pop()
            reduced = reduce(top_operator, left, right)
            self.domain.values.append(reduced)
            self._snapshot(f'{left} {top_operator} {right} = {reduced}')

        # Push the incoming term; it may still be waiting for something higher-precedence.
        self.domain.operators.append(operator)
        self.domain.values.append(float(operand))
        self._snapshot(f'pushed {operator} {operand}')

    def finalize(self, reduce):
        # Drain everything left, lowest-precedence last.
        while self.domain.operators:
            ...  # same reduction as above
        return self.domain.values[0]
```

Notice `reduce` is just a callable `ExpressionContext` is handed — it has no idea it's actually going to call `self.run('calc.multiply', ...)` under the hood. That's deliberately kept in the high-level context, one layer up, so this class stays a pure scheduling algorithm.

### 9.5 CalculatorAppContext: the fluent surface, and its routing slip

This is the `AppSessionContext` subclass you actually interact with. Every operator gets **two** distinct methods, not one overloaded one:

- A **starter** — two operands, begins a brand-new expression: `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`.
- A **continuation** — one operand, folds into the already-active expression: `add_to(x)`, `subtract_from(x)`, `multiply_by(x)`, `divide_by(x)`.

`multiply(a, b)` and `multiply_by(x)` are genuinely different operations — the first begins a chain from two numbers, the second assumes a chain already exists and extends it. Conflating them into one method with an optional second argument would hide that distinction; keeping them separate makes each call site self-documenting.

Now, how does a chain correlate the *several* `self.run(...)` calls its own reductions make (plus whatever the caller does in between) as belonging to the same chain? Rather than inventing a bespoke "expression id," we reach for something the request infrastructure already has: `RequestContext`/`Request` carry a `session_id`, auto-generated per call — but never threaded across calls by default. We extend it:

```python
class CalculatorAppContext(AppSessionContext):

    def __init__(self, ...):
        super().__init__(...)
        self._session_id = None   # no chain active yet

    def build_request(self, feature_id, headers={}, data={}):
        request = super().build_request(feature_id, headers, data)
        if self._session_id is not None:
            request.session_id = self._session_id   # stamp the chain's routing slip
        return request

    def _reduce(self, operator, left, right):
        feature_id = OPERATOR_FEATURE_MAP[operator]
        return self.run(feature_id, data=dict(a=left, b=right))

    def _start(self, operator, a, b):
        self._guard(self._session_id is None, EXPRESSION_ALREADY_ACTIVE_ID, ...)
        self._session_id = uuid.uuid4().hex
        expr = ExpressionContext.load(self.cache, self._session_id)
        expr.start(a)
        expr.apply_term(operator, b, reduce=self._reduce)
        expr.save(self.cache)
        return self

    def add(self, a, b):
        return self._start(ADD_OPERATOR, a, b)

    def add_to(self, x):
        return self._continue(ADD_OPERATOR, x)   # mirrors _start, requires an active chain

    @property
    def result(self):
        self._guard(self._session_id is not None, NO_ACTIVE_EXPRESSION_ID)
        expr = ExpressionContext.load(self.cache, self._session_id)
        value = expr.finalize(reduce=self._reduce)
        expr.discard(self.cache)
        self._session_id = None
        return value
```

That one id now does double duty: it's the `session_id` stamped on every request the chain issues, *and* the cache key `ExpressionContext` uses to find the chain's pending state. No parallel concept, just the request infrastructure's own correlation id, extended to also carry the chain's state around.

`subtract`/`multiply`/`divide` and their `_from`/`_by` continuations follow the exact same two patterns — see `app/contexts/calc.py` for the full set, plus `.reset()` (abandon a chain without evaluating it) and `.pending` (peek at the in-progress expression without finalizing it).

### 9.6 The new blueprint

With `CalculatorAppContext` written, we need something to actually construct one — the blueprint. It mirrors the CLI's own dedicated composition chain rather than `App(...)`'s, for the reason in 9.1.

**app/blueprints/calc.py**

```python
def build_calculator_app_context(app_session, cache) -> CalculatorAppContext:
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
    )

def create_calculator_app(interface_id='calc_fluent', config_file='config.yml') -> CalculatorAppContext:
    cache = core.build_cache()
    app_session = core.get_app_session(interface_id, cache, app_config=config_file)
    return build_calculator_app_context(app_session, cache)
```

Add the session to `config.yml`'s `sessions:` node (the same node `basic_calc` and `calc_cli` are already registered under):

```yaml
sessions:
  # ... existing sessions ...
  calc_fluent:
    name: Fluent Calculator
    description: >-
      A chainable, PEMDAS-aware calculator context. module_path/class_name
      below are informational only -- CalculatorAppContext is wired
      explicitly by app.blueprints.calc.create_calculator_app, not resolved
      from this config.
    module_path: app.contexts.calc
    class_name: CalculatorAppContext
```

Add two errors for the guard cases in `_start`/`_continue`/`result`:

```yaml
errors:
  # ... existing errors ...
  NO_ACTIVE_EXPRESSION:
    name: No Active Expression
    message:
      - lang: en_US
        text: 'No calculator expression is active; call add/subtract/multiply/divide to start a new chain.'
  EXPRESSION_ALREADY_ACTIVE:
    name: Expression Already Active
    message:
      - lang: en_US
        text: 'A calculator expression is already active; call .result or .reset() before starting a new one.'
```

No new `services:` or `features:` are needed — the fluent context reuses `calc.add`/`calc.subtract`/`calc.multiply`/`calc.divide` exactly as configured since Chapter 7.

### 9.7 See it work

**calc_fluent.py**

```python
from app.blueprints.calc import create_calculator_app
from tiferet import TiferetError

calc_app = create_calculator_app()

try:
    result = calc_app.add(1, 3).subtract_from(5).multiply_by(2).result
    print(f'1 + 3 - 5 * 2 = {result}')
except TiferetError as e:
    print(f'Error: {e.message}')

result = calc_app.add(2, 3).multiply_by(4).subtract_from(1).result
print(f'2 + 3 * 4 - 1 = {result}')

result = calc_app.multiply(3, 4).add_to(5).divide_by(2).result
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
1.0 + 3.0 = 4.0
5.0 * 2.0 = 10.0
4.0 - 10.0 = -6.0
3.0 * 4.0 = 12.0
2.0 + 12.0 = 14.0
14.0 - 1.0 = 13.0
3.0 * 4.0 = 12.0
5.0 / 2.0 = 2.5
12.0 + 2.5 = 14.5
```

Walk through the first chain by hand: `add(1, 3)` just pushes — nothing is pending yet to reduce. `subtract_from(5)` finds `'+'` at the top of the operator stack with precedence `>=` the incoming `'-'`, so it reduces `1 + 3` (a real `self.run('calc.add', ...)` call — that's the `1.0 + 3.0 = 4.0` line in the history) before pushing `'- 5'`. `multiply_by(2)` finds `'-'` with *lower* precedence than the incoming `'*'`, so it does **not** reduce — it just pushes, leaving both `'-'` and `'*'` pending. `.result` then drains the stack lowest-precedence-last: `5 * 2 = 10` first, then `4 - 10 = -6`. Every one of those reductions is a real feature call, which is why they all show up in the history, in exactly that order.

### 9.8 Recap

Across nine chapters you've now touched every layer Tiferet has: **domain** objects (`Formula`, `Expression`), **mappers** (`FormulaAggregate`/`FormulaConfigObject`), **interfaces** (`FormulaService`), **repos** (`FormulaConfigRepository`), **events** (arithmetic, history, formula, and reused arithmetic again), **assets** (operator constants), **contexts** (`ExpressionContext`, `CalculatorAppContext`), and **blueprints** (`create_calculator_app`) — all wired together through one consolidated `config.yml`.

The fluent context didn't require reinventing any arithmetic: it added a small scheduling layer on top of features you'd already built, and reused the framework's own request/session concept as the thread tying a multi-call chain together instead of inventing a parallel one. That's really the whole idea behind Tiferet's layering — each new capability should mostly be *composition*, not more special cases.

From here, natural next steps: exponentiation in the chain (right-associative, so the reduction rule needs a small tweak), a `.pending` tour through `history` for a "show your work" mode, or swapping the in-memory cache for something that survives process restarts.

You built a calculator that does long division on the order of operations. Nicely done.

→ Back to the **[tutorial index](index.md)**.
