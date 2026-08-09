# Errors – Three Exception Families and When Each Applies

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/assets/core.py`, `tiferet/interfaces/core.py`, `tiferet/domain/core.py`  
**Version:** 2.0.0

## Overview

Tiferet has **three unrelated exception families**, one per concern, and none of them extend one another. Reaching for the wrong one — most commonly, raising a `TiferetError` for an infrastructural failure so it can be "handled" — collapses a useful distinction the runtime relies on: only a `TiferetError` is catalogued, localized, resolvable to a `TiferetAPIError`, and skippable via a feature step's `pass_on_error`. The other two are deliberately uncatalogued and are expected to leak as unhandled exceptions.

**Vision:** See the `TiferetError` docstring in `tiferet/assets/core.py`, the `ServiceError` docstring in `tiferet/interfaces/core.py`, and the `ModelError` docstring in `tiferet/domain/core.py` for each family's value statement.

## Ubiquitous Language

- **Domain outcome** — a business-rule result the application is expected to communicate back to a caller (e.g. "feature not found"). The only kind of failure resolved through the error catalog.
- **Infrastructural failure** — a fault in configuration, I/O, or a lost connection. Not a domain outcome; not resolvable to a user-facing message.
- **Model defect** — an inconsistency *within* a single model instance (unknown field, invalid value, mutation-policy refusal). A consumer bug, not a runtime condition.
- **Catalogued error** — an `Error` domain object (see `docs/guides/domain/error.md`) resolvable by `error_code` through `ErrorContext`, formatted into a `TiferetAPIError`.
- **Provenance** — the `module_path` / `class_name` / `target_method` a `ServiceError` derives from the failing service instance and the calling frame, naming which service registration produced the failure.
- **Descriptor** — the serializable, reference-free summary of an offending model instance (`type`, `module`, plus any of `id`/`name`/`key` it declares), produced by `describe_model` (`tiferet/domain/core.py`).

## The Three Families at a Glance

| Family | Base | Raiser | Catalogued? | Caught by `run()` / skippable via `pass_on_error`? | Typical cause |
|---|---|---|---|---|---|
| `TiferetError` / `TiferetAPIError` | `Exception` (`assets/core.py`) | `TiferetError.raise_error(error_code, message, **kwargs)` | Yes — `assets/error.py` | Yes | A business-rule condition (`FEATURE_NOT_FOUND`, `REQUEST_VALIDATION_FAILED`) |
| `ServiceError` | `Exception` (`interfaces/core.py`) | `ServiceError.raise_for(service, error_code, message, cause=None, **kwargs)` | No — code lives beside the raise site | No — always propagates | A driver/library/config failure inside a `Service` implementation |
| `ModelError` | `Exception` (`domain/core.py`) | `ModelError.raise_error(...)` / `ModelError.raise_for_validation(...)` | No — uncatalogued by design | No — always propagates | An invalid mutation on an `Aggregate` |

None of the three extends another. A `except TiferetError:` block — the only kind `AppSessionContext.run` and `FeatureContext.execute_step`/`_execute_step_async` install — never catches a `ServiceError` or a `ModelError`. That is intentional: an infrastructural fault or a model defect reaching the top of the stack unhandled is the designed behavior, not a gap to close.

## `TiferetError` / `TiferetAPIError` — Domain Outcomes

`TiferetError` (`tiferet/assets/core.py`) is the base for every catalogued, resolvable domain outcome. `TiferetAPIError` extends it with `name` (defaulting to `error_code`) and `message`, and is already the formatted, consumer-facing shape.

- **Raising:** `TiferetError.raise_error(cls, error_code, message=None, **kwargs)` is a classmethod raiser — calling it on `TiferetError` raises a `TiferetError`; calling it on `TiferetAPIError` raises that subclass directly, since `raise cls(...)` dispatches to whichever class the method is invoked on.
- **Resolution flow:** `AppSessionContext.run` wraps feature execution in `except TiferetError as e: return self.handle_error(e, **kwargs)`. A `TiferetAPIError` passes through `handle_error` verbatim (it is already the formatted representation); any other `TiferetError` is resolved by the injected `raise_error_handler`, which looks up the matching `Error` domain object by `error_code` and calls `ErrorContext.format_response(error, exception, lang)` to produce the structured, localized response.
- **Skippability:** `FeatureContext.execute_step` / `_execute_step_async` catch `TiferetError` only; when a step sets `pass_on_error=True`, that — and only that — family resolves to `result = None` instead of propagating.
- **Catalog:** `assets/error.py`'s `CORE_DEFAULT_ERRORS` / `ADMIN_DEFAULT_ERRORS` hold **domain codes only** — every catalogued code has a raiser somewhere in `tiferet/`; no entries are pre-created for anticipated needs.

## `ServiceError` — Infrastructural Failures

`ServiceError` (`tiferet/interfaces/core.py`) lives beside `Service` rather than in the assets layer, because the failure is part of the service *contract* and every layer holding a service already imports `interfaces`.

- **Raising:** `ServiceError.raise_for(service, error_code, message=None, cause=None, **kwargs)` derives `module_path`/`class_name` from `type(service)` (or the class itself at a static raise site) and `target_method` from the calling frame — provenance is derived, not hand-passed, so a raise site never has to restate what it already knows about itself. `cause` makes `raise ... from cause` explicit rather than relying on `sys.exc_info()`.
- **Never catalogued:** each code is an `_ID` constant defined in the module that raises it, with an inline English-only f-string message — no localization, no `Error` domain object, no `ErrorContext` involvement. Representative hosts: `utils/file.py`, `utils/yaml.py`, `utils/json.py`, `utils/toml.py`, `utils/csv.py`, `utils/sqlite.py`, `repos/core.py`, `di/dependency_injector.py`.
- **Never caught:** neither `AppSessionContext.run` nor the feature-step executors catch anything but `TiferetError`, so a `ServiceError` always reaches the top of the stack as an unhandled exception — the intended behavior for a faulty connection or bad configuration.

## `ModelError` — Model Defects

`ModelError` (`tiferet/domain/core.py`) is read as a defect report rather than a response: it names the offending instance via a `model` descriptor (`describe_model`) rather than carrying request-facing context.

- **Two raisers:** `raise_error(error_code, message=None, model=None, **kwargs)` for a direct raise; `raise_for_validation(error: ValidationError, message=None, model=None, **kwargs)` classifies a Pydantic `ValidationError` itself — `INVALID_MODEL_ATTRIBUTE_ID` when any violation reports `no_such_attribute`, otherwise `INVALID_MODEL_VALUE_ID` — and chains the original `ValidationError` as the cause.
- **Primary call site:** `Aggregate.set_attribute` (`mappers/core.py`) wraps `setattr` and converts the resulting `ValidationError` via `raise_for_validation(error, model=self, ...)`; whitelist overrides on specific aggregates raise `ATTRIBUTE_NOT_SETTABLE` the same way.
- **Shared helper, two destinations:** `unpack_validation_error` (`domain/core.py`) flattens a Pydantic `ValidationError` into `{'field', 'type', 'message'}` violations, and is reused by **both** paths — but they resolve to different families. The mutation path (`Aggregate.set_attribute`) converts the violations into a `ModelError`. The request-validation path (`contexts/feature.py::validate_request`) uses the same flattening function directly and raises `REQUEST_VALIDATION_FAILED` as a **catalogued `TiferetError`** instead — a request payload failing validation is a domain outcome the caller needs resolved and localized; a mutated aggregate rejecting a bad `setattr` is a consumer bug that should surface as-is.

## Deciding Which Family to Raise

1. **Does the caller need this resolved to a localized, user-facing message?** → `TiferetError` (or `TiferetAPIError` directly, when the raise site already knows the consumer-facing `name`).
2. **Did a `Service` implementation fail for infrastructural reasons (I/O, driver, config, connection)?** → `ServiceError.raise_for(self, ...)`.
3. **Did an `Aggregate` mutation (or other model-level operation) produce an inconsistent instance?** → `ModelError.raise_error(...)` or `raise_for_validation(...)`.

If none of the above is true, the failure is likely a genuine bug — let it propagate as whatever exception it naturally is rather than forcing it into one of the three families.

## Boundaries

**Inside this domain:** which of the three exception families a given failure belongs to, how each is raised, and how (or whether) the runtime resolves it.
**Outside this domain:** the `Error` domain object's own shape and message-translation mechanics (`docs/guides/domain/error.md`), the `AppSessionContext.run` / `handle_error` orchestration flow (`docs/core/contexts.md`), and `ModelError`'s full vocabulary (`describe_model`, `unpack_validation_error`, identity fields — `docs/guides/domain/core.md`).

## Related Documentation

- [docs/guides/domain/core.md](domain/core.md) — `ModelError`, `describe_model`, `unpack_validation_error`, and `DomainObject`
- [docs/guides/domain/error.md](domain/error.md) — the catalogued `Error` domain object and message translation
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — `Service` and `ServiceError` code-style conventions
- [docs/core/assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md) — the error catalog's constants/factory conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
