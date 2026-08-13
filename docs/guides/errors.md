# Errors – Three Exception Families and When Each Applies

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/assets/core.py`, `tiferet/interfaces/core.py`, `tiferet/domain/core.py`  
**Version:** 2.0.0

## Overview

Tiferet has **three unrelated exception families**, one per concern, and none of them extend one another. Reaching for the wrong one — most commonly, raising a `TiferetError` for an infrastructural failure so it can be "handled" — collapses a useful distinction the runtime relies on: only a `TiferetError` is catalogued, localized, and resolvable to a `TiferetAPIError`. The other two are deliberately uncatalogued and are expected to leak as unhandled exceptions.

**Vision:** See the `TiferetError` docstring in `tiferet/assets/core.py`, the `ServiceError` docstring in `tiferet/interfaces/core.py`, and the `ModelError` docstring in `tiferet/domain/core.py` for each family's value statement.

## Ubiquitous Language

- **Domain outcome** — a business-rule result the application is expected to communicate back to a caller (e.g. "feature not found"). The only kind of failure resolved through the error catalog.
- **Infrastructural failure** — a fault in configuration, I/O, or a lost connection. Not a domain outcome; not resolvable to a user-facing message.
- **Model defect** — an inconsistency *within* a single model instance (unknown field, invalid value). A consumer bug, not a runtime condition.
- **Catalogued error** — an `Error` domain object (see [docs/guides/domain/error.md](domain/error.md)) resolvable by `error_code` through `ErrorContext`, formatted into a `TiferetAPIError`.
- **Provenance** — the `module_path` / `class_name` / `target_method` a `ServiceError` derives from the failing service instance and the calling frame, naming which service registration produced the failure.
- **Descriptor** — the serializable, reference-free summary of an offending model instance (`type`, `module`, plus any of `id`/`name`/`key` it declares), produced by `describe_model` (`tiferet/domain/core.py`).

## The Three Families at a Glance

| Family | Base | Raiser | Catalogued? | Caught by `AppSessionContext.run()`? | Typical cause |
|---|---|---|---|---|---|
| `TiferetError` / `TiferetAPIError` | `Exception` (`assets/core.py`) | `TiferetError.raise_error(error_code, message, **kwargs)` | Yes — `assets/error.py` | Yes | A business-rule condition (`FEATURE_NOT_FOUND`, `REQUEST_VALIDATION_FAILED`) |
| `ServiceError` | `Exception` (`interfaces/core.py`) | `ServiceError.raise_for(service, error_code, message, cause=None, **kwargs)` | No — code lives beside the raise site | No — always propagates | A driver/library/config failure inside a `Service` implementation |
| `ModelError` | `Exception` (`domain/core.py`) | `ModelError.raise_error(...)` / `ModelError.raise_for_validation(...)` | No — uncatalogued by design | No — always propagates | An invalid mutation on an `Aggregate` |

None of the three extends another. The only `except TiferetError:` block on the main execution path is inside `AppSessionContext.run` (`tiferet/contexts/app.py`) — it never catches a `ServiceError` or a `ModelError`. That is intentional: an infrastructural fault or a model defect reaching the top of the stack unhandled is the designed behavior, not a gap to close.

A separate, per-step `pass_on_error` flag on `FeatureContext.execute_step` / `_execute_step_async` (`tiferet/contexts/feature.py`) catches a bare `Exception` around that one step, so it will swallow *any* exception type raised inside the step — including a `ServiceError` or `ModelError` — not only a `TiferetError`. It is a step-level opt-in for skippable steps, and is a separate mechanism from `run()`'s top-level catch; it does not change which family is catalogued or resolved to a localized message.

## `TiferetError` / `TiferetAPIError` — Domain Outcomes
<a id="tiferet-error"></a>
<a id="tiferet-api-error"></a>

`TiferetError` (`tiferet/assets/core.py`) is the base for every catalogued, resolvable domain outcome. `TiferetAPIError` extends it with `name` (defaulting to `error_code`) and `message`, and is already the formatted, consumer-facing shape.

- **Raising:** `TiferetError.raise_error(cls, error_code, message=None, **kwargs)` is a classmethod raiser — calling it on `TiferetError` raises a `TiferetError`; calling it on `TiferetAPIError` raises that subclass directly, since `raise cls(...)` dispatches to whichever class the method is invoked on.
- **Resolution flow:** `AppSessionContext.run` (`tiferet/contexts/app.py`) wraps feature execution in `except TiferetError as e: return self.handle_error(e, **kwargs)`. `handle_error` delegates to the injected `raise_error_handler` closure (built by the `raise_error_handler`/`get_error` blueprints in `tiferet/blueprints/core.py`), which resolves the matching `Error` domain object by `error_code` (checking the shared cache first, falling back to the `get_error_evt`/`ErrorService` event on a miss) and calls `ErrorContext.format_response(error, exception)` to produce the structured response, then raises `TiferetAPIError(**formatted)`. Note this always re-resolves through the catalog — a `TiferetAPIError` raised directly is not special-cased to pass through verbatim.
- **Catalog:** `assets/error.py`'s `CORE_DEFAULT_ERRORS` holds **domain codes only** — every catalogued code has a raiser somewhere in `tiferet/`; no entries are pre-created for anticipated needs.

## `ServiceError` — Infrastructural Failures

`ServiceError` (`tiferet/interfaces/core.py`) lives beside `Service` rather than in the assets layer, because the failure is part of the service *contract* and every layer holding a service already imports `interfaces`.

- **Raising:** `ServiceError.raise_for(service, error_code, message=None, cause=None, **kwargs)` derives `module_path`/`class_name` from `type(service)` (or the class itself at a static raise site) and `target_method` from the calling frame — provenance is derived, not hand-passed, so a raise site never has to restate what it already knows about itself. `cause` makes `raise ... from cause` explicit rather than relying on `sys.exc_info()`.
- **Never catalogued:** each code is an `_ID` constant defined in the module that raises it, with an inline English-only f-string message — no localization, no `Error` domain object, no `ErrorContext` involvement. Representative hosts: `utils/file.py`, `utils/yaml.py`, `utils/json.py`, `utils/toml.py`, `utils/csv.py`, `utils/sqlite.py`, `repos/core.py`.
- **Never caught:** `AppSessionContext.run` catches only `TiferetError`, so a `ServiceError` always reaches the top of the stack as an unhandled exception unless a step's `pass_on_error` flag suppresses it — the intended behavior for a faulty connection or bad configuration.

## `ModelError` — Model Defects

`ModelError` (`tiferet/domain/core.py`) is read as a defect report rather than a response: it names the offending instance via a `model` descriptor (`describe_model`) rather than carrying request-facing context.

- **Two raisers:** `raise_error(error_code, message=None, model=None, **kwargs)` for a direct raise; `raise_for_validation(error: ValidationError, message=None, model=None, **kwargs)` classifies a Pydantic `ValidationError` itself — `INVALID_MODEL_ATTRIBUTE_ID` when any violation reports `no_such_attribute`, otherwise `INVALID_MODEL_VALUE_ID` — and chains the original `ValidationError` as the cause.
- **Primary call site:** `Aggregate.set_attribute` (`tiferet/mappers/core.py`) wraps `setattr` and converts the resulting `ValidationError` via `raise_for_validation(error, model=self, attribute=attribute)`.
- **A twin, not a shared call:** `unpack_validation_error` (`domain/core.py`) flattens a Pydantic `ValidationError` into `{'field', 'type', 'message'}` violations, and is called by the mutation path (`raise_for_validation`, above). The request-validation path — `RequestSpecification.validate` (`tiferet/domain/feature.py`) — implements the **same flattening logic inline** rather than calling `unpack_validation_error` directly, and raises `REQUEST_VALIDATION_FAILED` as a **catalogued `TiferetError`** instead of a `ModelError`. The two paths resolve to different families for the same reason they duplicate the flattening shape: a request payload failing validation is a domain outcome the caller needs resolved and localized, while a mutated aggregate rejecting a bad `setattr` is a consumer bug that should surface as-is.

## Deciding Which Family to Raise

1. **Does the caller need this resolved to a localized, user-facing message?** → `TiferetError` (or `TiferetAPIError` directly, when the raise site already knows the consumer-facing `name`).
2. **Did a `Service` implementation fail for infrastructural reasons (I/O, driver, config, connection)?** → `ServiceError.raise_for(self, ...)`.
3. **Did an `Aggregate` mutation (or other model-level operation) produce an inconsistent instance?** → `ModelError.raise_error(...)` or `raise_for_validation(...)`.

If none of the above is true, the failure is likely a genuine bug — let it propagate as whatever exception it naturally is rather than forcing it into one of the three families.

## Boundaries

**Inside this domain:** which of the three exception families a given failure belongs to, how each is raised, and how (or whether) the runtime resolves it.
**Outside this domain:** the `Error` domain object's own shape and message-translation mechanics ([docs/guides/domain/error.md](domain/error.md)), the `AppSessionContext.run` / `handle_error` orchestration flow ([docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md)), and `ModelError`'s full vocabulary (`describe_model`, `unpack_validation_error`, identity fields — [docs/guides/domain/core.md](domain/core.md)).

## Related Documentation

- [docs/guides/domain/core.md](domain/core.md) — `ModelError`, `describe_model`, `unpack_validation_error`, and `DomainObject`
- [docs/guides/domain/error.md](domain/error.md) — the catalogued `Error` domain object and message translation
- [docs/guides/interfaces.md](interfaces.md) — `Service` and `ServiceError` design conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — `Service` code-style conventions
- [docs/core/assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md) — the error catalog's constants/factory conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
