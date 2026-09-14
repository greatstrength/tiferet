# Domain – Logging: Formatter, Handler, Logger, and LoggingSettings

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0

## Overview

The Logging domain defines the structural foundation for observability and logging configuration in Tiferet. Logging configuration is expressed as three composable domain objects — `Formatter`, `Handler`, and `Logger` — that together describe how log messages are formatted, where they are sent, and which loggers are active at what level.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries via `format_config()`. All state changes (renaming, adding/removing handlers, etc.) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/logging.py`

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

| Attribute     | Type            | Required | Default | Description                          |
|---------------|-----------------|----------|---------|--------------------------------------|
| `id`          | `str`           | Yes      | —       | The unique identifier of the formatter. |
| `name`        | `str`           | Yes      | —       | The name of the formatter.           |
| `description` | `str \| None`   | No       | `None`  | The description of the formatter.    |
| `format`      | `str`           | Yes      | —       | The format string for log messages.  |
| `datefmt`     | `str \| None`   | No       | `None`  | The date format for log timestamps.  |

#### Methods

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

| Attribute     | Type            | Required | Default | Description                                              |
|---------------|-----------------|----------|---------|----------------------------------------------------------|
| `id`          | `str`           | Yes      | —       | The unique identifier of the handler.                    |
| `name`        | `str`           | Yes      | —       | The name of the handler.                                 |
| `description` | `str \| None`   | No       | `None`  | The description of the handler.                          |
| `module_path` | `str`           | Yes      | —       | The module path for the handler class.                   |
| `class_name`  | `str`           | Yes      | —       | The class name of the handler.                           |
| `level`       | `str`           | Yes      | —       | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `formatter`   | `str`           | Yes      | —       | The ID of the formatter to use.                          |
| `stream`      | `str \| None`   | No       | `None`  | The stream for StreamHandler (e.g., `ext://sys.stdout`). |
| `filename`    | `str \| None`   | No       | `None`  | The file path for FileHandler (e.g., `app.log`).         |

#### Methods

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

| Attribute     | Type             | Required | Default | Description                                              |
|---------------|------------------|----------|---------|----------------------------------------------------------|
| `id`          | `str`            | Yes      | —       | The unique identifier of the logger.                     |
| `name`        | `str`            | Yes      | —       | The name of the logger.                                  |
| `description` | `str \| None`    | No       | `None`  | The description of the logger.                           |
| `level`       | `str`            | Yes      | —       | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `handlers`    | `List[str]`      | No       | `[]`    | List of handler IDs for the logger.                      |
| `propagate`   | `bool`           | No       | `False` | Whether to propagate messages to parent loggers.         |
| `is_root`     | `bool`           | No       | `False` | Whether this is the root logger.                         |

#### Methods

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
| `formatters` | `List[Formatter]` | No | `[]` | The formatter configurations. |
| `handlers` | `List[Handler]` | No | `[]` | The handler configurations. |
| `loggers` | `List[Logger]` | No | `[]` | The logger configurations. |
| `version` | `int` | No | `1` | The dictConfig schema version. |
| `disable_existing_loggers` | `bool` | No | `False` | Whether to disable existing loggers on configuration. |

#### Methods

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

1. The session hub calls `AppSessionContext.build_logger()`, which delegates to the injected `build_logger_handler` (required fifth handler — there is no long-lived `logging_context` constructor keyword on the hub).
2. `blueprints/core.py::build_logger_handler` checks the shared cache under `LOGGER_CACHE_PREFIX` (`('logging', 'loggers')`) for a previously built logger id.
3. On a miss, `logging_list_all_evt` loads repository `Formatter` / `Handler` / `Logger` objects; `merge_logging_settings` merges them over cache-seeded defaults by `.id`.
4. `LoggingContext.from_domain(settings, logger_id=...)` binds the merged `LoggingSettings`; `LoggingContext.build_logger` calls `LoggingSettings.format_config()` and `create_logger`.
5. The built logger is stored under `LOGGER_CACHE_PREFIX` so `dictConfig` runs once per logger id per process.

Logging CRUD (`logging.add_formatter` / `remove_formatter`, `logging.add_handler` / `remove_handler`, `logging.add_logger` / `remove_logger`, and `logging.list`) is one of the six admin catalog domains managed by `AdminApp` / `AdminCLI`. See [docs/guides/admin.md](../admin.md) for the full management surface and worked examples.

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

The following domain events interact with `Formatter`, `Handler`, and `Logger`:

| Event                     | Description                                           |
|---------------------------|-------------------------------------------------------|
| `ListAllLoggingConfigs`   | Retrieves all formatters, handlers, and loggers in one call (wired as `logging_list_all_evt`). |
| `AddFormatter`            | Creates and persists a new `Formatter`.               |
| `AddHandler`              | Creates and persists a new `Handler`.                 |
| `AddLogger`               | Creates and persists a new `Logger`.                  |
| `RemoveFormatter` / `RemoveHandler` / `RemoveLogger` | Idempotent removals used by admin CRUD. |

These events depend on the `LoggingService` interface for persistence operations.

## Service Interface

**`LoggingService`** (`tiferet/interfaces/logging.py`) defines the abstract contract for Logging domain persistence:

- `list_all() -> Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]`
- `save_formatter(formatter: FormatterAggregate) -> None`
- `save_handler(handler: HandlerAggregate) -> None`
- `save_logger(logger: LoggerAggregate) -> None`
- `delete_formatter(formatter_id: str) -> None`
- `delete_handler(handler_id: str) -> None`
- `delete_logger(logger_id: str) -> None`

The read side is a **single** `list_all()` returning all three collections as one tuple, not three separate list methods — the three sections are always loaded together, so one call avoids three reads of the same file. As elsewhere, the contract is typed with aggregates rather than the bare value objects, since a caller retrieving a configuration is generally about to mutate and re-save it.

Concrete implementations (e.g., `LoggingConfigRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** Logger construction is a first-class hub template method (`build_logger` / `build_logger_handler`). Every application session can select its own `logger_id` and logging configuration.
- **Blueprints:** `merge_logging_settings` and `build_logger_handler` in `tiferet/blueprints/core.py` own the list → merge → cache path; `LoggingContext` remains the ephemeral assembler.
- **Admin:** Logging CRUD is one of the six admin catalog domains — see [docs/guides/admin.md](../admin.md).
- **All Contexts:** Once configured, the Python logging system is available globally to all contexts, domain events, and services throughout the application lifecycle.

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

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
- [docs/guides/domain/error.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/error.md) — Error domain guide
- [docs/guides/domain/feature.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/feature.md) — Feature domain guide
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service contract definitions
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns & testing
- [docs/guides/admin.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/admin.md) — Admin Logging CRUD domain
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — `build_logger_handler` five-handler slot
