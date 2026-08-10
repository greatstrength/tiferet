# Domain – Logging: Formatter, Handler, Logger, and LoggingSettings

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

The Logging domain defines the structural foundation for observability and logging configuration in Tiferet. Logging configuration is expressed as three composable domain objects — `Formatter`, `Handler`, and `Logger` — that together describe how log messages are formatted, where they are sent, and which loggers are active at what level.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries via `format_config()`. All state changes (renaming, adding/removing handlers, etc.) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/logging.py`
**Vision:** See the `LoggingSettings` class docstring in `tiferet/domain/logging.py` for the value statement this guide distills.

## Ubiquitous Language

- **dictConfig entry** — the plain-dict shape each domain object's `format_config()` produces, matching the structure `logging.config.dictConfig` expects for that section.
- **Root logger** — the one `Logger` in a `LoggingSettings` bundle flagged `is_root`; `LoggingSettings.format_config()` draws the dedicated `root` dictConfig entry from it and excludes it from the keyed `loggers` mapping.
- **Whole-system assembly** — `LoggingSettings.format_config()`'s role: composing every bundled `Formatter`/`Handler`/`Logger`'s own `format_config()` into the single dictionary `logging.config.dictConfig` consumes.

## Three-Model Composition

The Logging domain follows a three-model composition pattern:

1. **Formatter** defines how log messages are formatted (format string, date format).
2. **Handler** defines where log messages are sent (console, file), at what level, and references a `Formatter` by ID.
3. **Logger** defines a named logger with a level, a list of `Handler` IDs, and propagation behavior.

At runtime, the `LoggingSettings` value object bundles the formatters, handlers, and loggers and owns the assembly: its `format_config()` calls `format_config()` on each bundled domain object and composes the results into the standard Python `logging.config.dictConfig` structure. `LoggingContext.build_logger` builds the `LoggingSettings` (applying the built-in defaults as the per-section fallback) and passes its assembled config to `create_logger`.

```
Logger → [handler_id, ...] → Handler → formatter_id → Formatter
```

## Domain Objects

### Formatter

Immutable value object representing a logging formatter configuration.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="formatter-id"></a>`id` | `str` | Yes | — | The unique identifier of the formatter. |
| <a id="formatter-name"></a>`name` | `str` | Yes | — | The name of the formatter. |
| <a id="formatter-description"></a>`description` | `str \| None` | No | `None` | The description of the formatter. |
| <a id="formatter-format"></a>`format` | `str` | Yes | — | The format string for log messages. |
| <a id="formatter-datefmt"></a>`datefmt` | `str \| None` | No | `None` | The date format for log timestamps. |

#### Methods

<a id="formatter-format-config"></a>
**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible formatter entry:

```python
formatter = Formatter(id='simple', name='Simple',
    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d')
formatter.format_config()
# {'format': '%(asctime)s - %(message)s', 'datefmt': '%Y-%m-%d'}
```

When `datefmt` is not set, the key is still present with a `None` value.

### Handler

Immutable value object representing a logging handler configuration.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="handler-id"></a>`id` | `str` | Yes | — | The unique identifier of the handler. |
| <a id="handler-name"></a>`name` | `str` | Yes | — | The name of the handler. |
| <a id="handler-description"></a>`description` | `str \| None` | No | `None` | The description of the handler. |
| <a id="handler-module-path"></a>`module_path` | `str` | Yes | — | The module path for the handler class. |
| <a id="handler-class-name"></a>`class_name` | `str` | Yes | — | The class name of the handler. |
| <a id="handler-level"></a>`level` | `str` | Yes | — | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| <a id="handler-formatter"></a>`formatter` | `str` | Yes | — | The ID of the formatter to use. |
| <a id="handler-stream"></a>`stream` | `str \| None` | No | `None` | The stream for StreamHandler (e.g., `ext://sys.stdout`). |
| <a id="handler-filename"></a>`filename` | `str \| None` | No | `None` | The file path for FileHandler (e.g., `app.log`). |

#### Methods

<a id="handler-format-config"></a>
**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible handler entry. The `class` key is composed from `module_path` and `class_name`. Optional attributes (`stream`, `filename`) are only included when set:

```python
handler = Handler(id='console', name='Console',
    module_path='logging', class_name='StreamHandler',
    level='INFO', formatter='simple', stream='ext://sys.stdout')
handler.format_config()
# {'class': 'logging.StreamHandler', 'level': 'INFO', 'formatter': 'simple', 'stream': 'ext://sys.stdout'}
```

### Logger

Immutable value object representing a logger configuration.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="logger-id"></a>`id` | `str` | Yes | — | The unique identifier of the logger. |
| <a id="logger-name"></a>`name` | `str` | Yes | — | The name of the logger. |
| <a id="logger-description"></a>`description` | `str \| None` | No | `None` | The description of the logger. |
| <a id="logger-level"></a>`level` | `str` | Yes | — | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| <a id="logger-handlers"></a>`handlers` | `List[str]` | No | `[]` | List of handler IDs for the logger. |
| <a id="logger-propagate"></a>`propagate` | `bool` | No | `False` | Whether to propagate messages to parent loggers. |
| <a id="logger-is-root"></a>`is_root` | `bool` | No | `False` | Whether this is the root logger. |

#### Methods

<a id="logger-format-config"></a>
**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible logger entry:

```python
logger = Logger(id='app', name='App Logger',
    level='DEBUG', handlers=['console'], propagate=True)
logger.format_config()
# {'level': 'DEBUG', 'handlers': ['console'], 'propagate': True}
```

### LoggingSettings

Runtime value object that bundles the formatter, handler, and logger configurations and owns the whole-system `dictConfig` assembly. It is runtime-only — there is no Aggregate or TransferObject counterpart — and is intentionally logger-agnostic (the final `getLogger` call and its `logger_id` stay with `LoggingContext`).

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="loggingsettings-formatters"></a>`formatters` | `List[Formatter]` | No | `[]` | The formatter configurations. |
| <a id="loggingsettings-handlers"></a>`handlers` | `List[Handler]` | No | `[]` | The handler configurations. |
| <a id="loggingsettings-loggers"></a>`loggers` | `List[Logger]` | No | `[]` | The logger configurations. |
| <a id="loggingsettings-version"></a>`version` | `int` | No | `1` | The dictConfig schema version. |
| <a id="loggingsettings-disable-existing-loggers"></a>`disable_existing_loggers` | `bool` | No | `False` | Whether to disable existing loggers on configuration. |

#### Methods

<a id="loggingsettings-format-config"></a>
**`format_config() -> Dict[str, Any]`**

Assembles a `logging.config.dictConfig`-compatible dictionary, keying `formatters`/`handlers`/`loggers` by id and drawing the `root` entry from the logger flagged `is_root`:

```python
settings = LoggingSettings(formatters=[fmt], handlers=[hdlr], loggers=[root_logger])
settings.format_config()
# {'version': 1, 'disable_existing_loggers': False, 'formatters': {...},
#  'handlers': {...}, 'loggers': {...}, 'root': {...}}
```

## Built-In Defaults

Tiferet provides built-in logging defaults in `assets/logging.py`. These define a standard console formatter, stream handler, and root logger that are used when no application-specific logging configuration is provided.

## Runtime Role

The Logging domain objects participate in runtime configuration through the following flow:

1. `LoggingContext.build_logger()` is called during application interface initialization.
2. `LoggingService` loads all `Formatter`, `Handler`, and `Logger` domain objects from `logging.yml`.
3. `LoggingContext.build_logger` wraps the loaded formatters, handlers, and loggers in a `LoggingSettings` value object (applying the built-in defaults as the per-section fallback).
4. `LoggingSettings.format_config()` assembles a complete `dictConfig` dictionary with `formatters`, `handlers`, `loggers`, and `root` sections.
5. `logging.config.dictConfig(config)` is called to configure the Python logging system.
6. The configured logger is available for use throughout the application.

## Configuration Mapping

Logging is configured in the `logging` section of the configuration file (typically `config.yml`, though per-file configs such as `logging.yml` are also supported):

```yaml
formatters:
  simple:
    name: Simple Formatter
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

handlers:
  console:
    name: Console Handler
    module_path: logging
    class_name: StreamHandler
    level: INFO
    formatter: simple
    stream: ext://sys.stdout

loggers:
  app:
    name: App Logger
    level: DEBUG
    handlers:
      - console
    propagate: false
```

Each top-level section (`formatters`, `handlers`, `loggers`) maps directly to the corresponding domain object type.

## Domain Events

The following domain events (`tiferet/events/logging.py`) interact with `Formatter`, `Handler`, and `Logger`:

| Event | Description |
|---|---|
| `ListAllLoggingConfigs` | Retrieves all formatters, handlers, and loggers as a single tuple. |
| `AddFormatter` | Creates and persists a new `Formatter`. |
| `RemoveFormatter` | Removes a `Formatter` by ID (idempotent). |
| `AddHandler` | Creates and persists a new `Handler`. |
| `RemoveHandler` | Removes a `Handler` by ID (idempotent). |
| `AddLogger` | Creates and persists a new `Logger`. |
| `RemoveLogger` | Removes a `Logger` by ID (idempotent). |

These events depend on the `LoggingService` interface for persistence operations.

## Service Interface

**`LoggingService`** (`tiferet/interfaces/logging.py`) defines the abstract contract for Logging domain persistence:

- `list_all() -> Tuple[List[Formatter], List[Handler], List[Logger]]`
- `save_formatter(formatter: FormatterAggregate) -> None`
- `save_handler(handler: HandlerAggregate) -> None`
- `save_logger(logger: LoggerAggregate) -> None`
- `delete_formatter(formatter_id: str) -> None`
- `delete_handler(handler_id: str) -> None`
- `delete_logger(logger_id: str) -> None`

Concrete implementations (e.g., `LoggingConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `LoggingContext` is loaded lazily by the `AppSessionContext` hub's `build_logger` template method (via `build_logger_handler`), receiving `LoggingService` via dependency injection. Every app session can have its own logging configuration.
- **All Contexts:** Once configured, the Python logging system is available globally to all contexts, domain events, and services throughout the application lifecycle.

## Boundaries

**Inside this domain:** the declared shape of formatter/handler/logger configuration and the pure `dictConfig` assembly logic (`format_config()` on each object, and the whole-system assembly on `LoggingSettings`).
**Outside this domain:** the actual `logging.config.dictConfig(...)` call and `getLogger` construction (`LoggingContext`/`create_logger`, `docs/core/contexts.md`), and cache-first logger reuse (the `('logging', 'loggers')` cache prefix owned by `contexts/app.py::build_logger_handler`).

## Instantiation

```python
from tiferet.domain import Formatter, Handler, Logger

fmt = Formatter(
    id='simple',
    name='Simple Formatter',
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d',
)

hdlr = Handler(
    id='console',
    name='Console Handler',
    module_path='logging',
    class_name='StreamHandler',
    level='INFO',
    formatter='simple',
    stream='ext://sys.stdout',
)

lgr = Logger(
    id='app',
    name='App Logger',
    level='DEBUG',
    handlers=['console'],
    propagate=False,
)

# fmt.format_config()  == {'format': '%(asctime)s - %(message)s', 'datefmt': '%Y-%m-%d'}
# hdlr.format_config() == {'class': 'logging.StreamHandler', 'level': 'INFO', 'formatter': 'simple', 'stream': 'ext://sys.stdout'}
# lgr.format_config()  == {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False}
```

## Related Documentation

- [docs/guides/domain/app.md](app.md) — App domain guide (`build_logger_handler` wiring)
- [docs/guides/domain/error.md](error.md) — Error domain guide
- [docs/guides/domain/feature.md](feature.md) — Feature domain guide
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
