```markdown
# Domain – Logging: Formatter, Handler, and Logger

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 06, 2026  
**Version:** 2.0.0a2

## Overview

The Logging domain defines the structural foundation for observability and logging configuration in Tiferet. Logging configuration is expressed as three composable domain objects — `Formatter`, `Handler`, and `Logger` — that together describe how log messages are formatted, where they are sent, and which loggers are active at what level.

All domain objects in this module are **immutable value objects**: they carry no mutation methods and expose only read-only queries via `format_config()`. All state changes (renaming, adding/removing handlers, etc.) occur exclusively through Aggregates in the mappers layer.

**Module:** `tiferet/domain/logging.py`

## Three-Model Composition

The Logging domain follows a three-model composition pattern:

1. **Formatter** defines how log messages are formatted (format string, date format).
2. **Handler** defines where log messages are sent (console, file), at what level, and references a `Formatter` by ID.
3. **Logger** defines a named logger with a level, a list of `Handler` IDs, and propagation behavior.

At runtime, `LoggingContext` assembles these into a `dictConfig`-compatible dictionary by calling `format_config()` on each domain object and composing the results into the standard Python `logging.config.dictConfig` structure.

```
Logger → [handler_id, ...] → Handler → formatter_id → Formatter
```

## Domain Objects

### Formatter

Immutable value object representing a logging formatter configuration.

| Attribute     | Type         | Required | Default | Description                          |
|---------------|--------------|----------|---------|--------------------------------------|
| `id`          | `StringType` | Yes      | —       | The unique identifier of the formatter. |
| `name`        | `StringType` | Yes      | —       | The name of the formatter.           |
| `description` | `StringType` | No       | —       | The description of the formatter.    |
| `format`      | `StringType` | Yes      | —       | The format string for log messages.  |
| `datefmt`     | `StringType` | No       | —       | The date format for log timestamps.  |

#### Methods

**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible formatter entry:

```python
formatter = DomainObject.new(Formatter, id='simple', name='Simple',
    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d')
formatter.format_config()
# {'format': '%(asctime)s - %(message)s', 'datefmt': '%Y-%m-%d'}
```

When `datefmt` is not set, the key is still present with a `None` value.

### Handler

Immutable value object representing a logging handler configuration.

| Attribute     | Type         | Required | Default | Description                                              |
|---------------|--------------|----------|---------|----------------------------------------------------------|
| `id`          | `StringType` | Yes      | —       | The unique identifier of the handler.                    |
| `name`        | `StringType` | Yes      | —       | The name of the handler.                                 |
| `description` | `StringType` | No       | —       | The description of the handler.                          |
| `module_path` | `StringType` | Yes      | —       | The module path for the handler class.                   |
| `class_name`  | `StringType` | Yes      | —       | The class name of the handler.                           |
| `level`       | `StringType` | Yes      | —       | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `formatter`   | `StringType` | Yes      | —       | The ID of the formatter to use.                          |
| `stream`      | `StringType` | No       | —       | The stream for StreamHandler (e.g., `ext://sys.stdout`). |
| `filename`    | `StringType` | No       | —       | The file path for FileHandler (e.g., `app.log`).         |

#### Methods

**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible handler entry. The `class` key is composed from `module_path` and `class_name`. Optional attributes (`stream`, `filename`) are only included when set:

```python
handler = DomainObject.new(Handler, id='console', name='Console',
    module_path='logging', class_name='StreamHandler',
    level='INFO', formatter='simple', stream='ext://sys.stdout')
handler.format_config()
# {'class': 'logging.StreamHandler', 'level': 'INFO', 'formatter': 'simple', 'stream': 'ext://sys.stdout'}
```

### Logger

Immutable value object representing a logger configuration.

| Attribute     | Type                   | Required | Default | Description                                              |
|---------------|------------------------|----------|---------|----------------------------------------------------------|
| `id`          | `StringType`           | Yes      | —       | The unique identifier of the logger.                     |
| `name`        | `StringType`           | Yes      | —       | The name of the logger.                                  |
| `description` | `StringType`           | No       | —       | The description of the logger.                           |
| `level`       | `StringType`           | Yes      | —       | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `handlers`    | `ListType(StringType)` | No       | `[]`    | List of handler IDs for the logger.                      |
| `propagate`   | `BooleanType`          | No       | `False` | Whether to propagate messages to parent loggers.         |
| `is_root`     | `BooleanType`          | No       | `False` | Whether this is the root logger.                         |

#### Methods

**`format_config() -> Dict[str, Any]`**

Returns a `dictConfig`-compatible logger entry:

```python
logger = DomainObject.new(Logger, id='app', name='App Logger',
    level='DEBUG', handlers=['console'], propagate=True)
logger.format_config()
# {'level': 'DEBUG', 'handlers': ['console'], 'propagate': True}
```

## Built-In Defaults

Tiferet provides built-in logging defaults in `assets/logging.py`. These define a standard console formatter, stream handler, and root logger that are used when no application-specific logging configuration is provided.

## Runtime Role

The Logging domain objects participate in runtime configuration through the following flow:

1. `LoggingContext.build_logger()` is called during application interface initialization.
2. `LoggingService` loads all `Formatter`, `Handler`, and `Logger` domain objects from `logging.yml`.
3. `LoggingContext` calls `format_config()` on each domain object to produce `dictConfig`-compatible entries.
4. The results are assembled into a complete `dictConfig` dictionary with `formatters`, `handlers`, and `loggers` sections.
5. `logging.config.dictConfig(config)` is called to configure the Python logging system.
6. The configured logger is available for use throughout the application.

## Configuration Mapping

Logging is configured in `app/configs/logging.yml`:

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
| `ListAllLoggingConfigs`   | Retrieves all formatters, handlers, and loggers.      |
| `AddFormatter`            | Creates and persists a new `Formatter`.               |
| `AddHandler`              | Creates and persists a new `Handler`.                 |
| `AddLogger`               | Creates and persists a new `Logger`.                  |

These events depend on the `LoggingService` interface for persistence operations.

## Service Interface

**`LoggingService`** (`tiferet/interfaces/logging.py`) defines the abstract contract for Logging domain persistence:

- `list_formatters() -> List[Formatter]`
- `list_handlers() -> List[Handler]`
- `list_loggers() -> List[Logger]`
- `save_formatter(formatter) -> None`
- `save_handler(handler) -> None`
- `save_logger(logger) -> None`

Concrete implementations (e.g., `LoggingYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `LoggingContext` is loaded as part of the application interface bootstrap, receiving `LoggingService` via dependency injection. Every application interface can have its own logging configuration.
- **All Contexts:** Once configured, the Python logging system is available globally to all contexts, domain events, and services throughout the application lifecycle.

## Instantiation

```python
from tiferet.domain import DomainObject, Formatter, Handler, Logger

fmt = DomainObject.new(
    Formatter,
    id='simple',
    name='Simple Formatter',
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d',
)

hdlr = DomainObject.new(
    Handler,
    id='console',
    name='Console Handler',
    module_path='logging',
    class_name='StreamHandler',
    level='INFO',
    formatter='simple',
    stream='ext://sys.stdout',
)

lgr = DomainObject.new(
    Logger,
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
```
