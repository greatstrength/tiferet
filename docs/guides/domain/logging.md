# Domain – Logging (Observability)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** May 04, 2026  
**Version:** 2.0.0b1

## Overview

The Logging domain defines **how execution is observed**. It provides a configuration-driven approach to Python's `logging` module, representing formatters, handlers, and loggers as domain objects that can be managed through YAML configuration and domain events — just like any other Tiferet domain concept.

The Logging domain uses a three-model composition: `Formatter` defines how log messages are formatted, `Handler` defines where they go (console, file, etc.), and `Logger` ties them together with a log level and propagation rules. At runtime, `LoggingContext` loads these objects, converts them to a `dictConfig`-compatible dictionary, and produces a live `logging.Logger` instance.

## Domain Objects

### Formatter

Defines the format string and date format for log messages.

| Attribute     | Type            | Required | Default | Description                          |
|---------------|-----------------|----------|---------|--------------------------------------|
| `id`          | `str`           | Yes      | —       | The unique identifier of the formatter. |
| `name`        | `str`           | Yes      | —       | The name of the formatter.           |
| `description` | `str \| None`   | No       | `None`  | The description of the formatter.    |
| `format`      | `str`           | Yes      | —       | The format string for log messages.  |
| `datefmt`     | `str \| None`   | No       | `None`  | The date format for log timestamps.  |

**Behavior method:**

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

Defines a log destination — where messages are sent and at what level. References a `Formatter` by ID.

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

**Behavior method:**

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

Defines a logger configuration — its level, which handlers it uses, and whether it propagates to parent loggers.

| Attribute     | Type             | Required | Default | Description                                              |
|---------------|------------------|----------|---------|----------------------------------------------------------|
| `id`          | `str`            | Yes      | —       | The unique identifier of the logger.                     |
| `name`        | `str`            | Yes      | —       | The name of the logger.                                  |
| `description` | `str \| None`    | No       | `None`  | The description of the logger.                           |
| `level`       | `str`            | Yes      | —       | The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `handlers`    | `List[str]`      | No       | `[]`    | List of handler IDs for the logger.                      |
| `propagate`   | `bool`           | No       | `False` | Whether to propagate messages to parent loggers.         |
| `is_root`     | `bool`           | No       | `False` | Whether this is the root logger.                         |

**Behavior method:**

- `format_config()` — returns a dict with `level`, `handlers`, and `propagate` keys.

### Three-Model Composition

```python
logger = Logger(id='app', name='App Logger',
    level='DEBUG', handlers=['console'], propagate=True)
logger.format_config()
# {'level': 'DEBUG', 'handlers': ['console'], 'propagate': True}
```

A `Logger` with `handlers: ['console', 'file']` uses two `Handler` objects, each of which references a `Formatter` by ID. This composition is resolved by `LoggingContext.format_config()`, which assembles all three layers into a single `dictConfig`-compatible dictionary.

## Built-in Defaults

The framework provides default logging configurations in `assets/logging.py`:

- **Default formatter** — `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Default handler** — `StreamHandler` to `sys.stdout` at `DEBUG` level
- **Default logger** — `DEBUG` level with the default handler, non-propagating

These defaults are used by `LoggingContext.build_logger()` when no logging configuration is defined in `logging.yml`. This ensures every app interface has basic logging even without explicit configuration.

## Runtime Role

`LoggingContext` is the sole consumer of the Logging domain at runtime:

1. **`build_logger()`** loads all formatters, handlers, and loggers via `ListAllLoggingConfigs`.
2. If any category is empty, **defaults from `assets/logging.py`** are substituted as `DomainObject.new(Formatter, ...)`, etc.
3. **`format_config(formatters, handlers, loggers)`** calls each model's `format_config()` method and assembles the result into a `dictConfig`-compatible dictionary:
   - `formatters` — keyed by formatter ID
   - `handlers` — keyed by handler ID
   - `loggers` — keyed by logger ID (excluding root)
   - `root` — the logger with `is_root=True`, if any
4. **`create_logger(logger_id, logging_config)`** applies `logging.config.dictConfig()` and returns `logging.getLogger(logger_id)`.

The resulting logger is used throughout the request lifecycle — from parsing to feature execution to response handling.

## Configuration

Logging is defined in `app/configs/logging.yml`:

```yaml
formatters:
  default:
    name: Default Formatter
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

handlers:
  console:
    name: Console Handler
    module_path: logging
    class_name: StreamHandler
    level: DEBUG
    formatter: default
    stream: ext://sys.stdout

loggers:
  default:
    name: Default Logger
    level: DEBUG
    handlers:
      - console
    propagate: false
```

Each section maps to the corresponding domain object type, keyed by ID.

## Domain Events

| Event | Purpose |
|-------|---------|
| `ListAllLoggingConfigs` | Retrieve all formatters, handlers, and loggers (used during logger build) |
| `AddFormatter` | Create a new formatter configuration |
| `RemoveFormatter` | Delete a formatter configuration |
| `AddHandler` | Create a new handler configuration |
| `RemoveHandler` | Delete a handler configuration |
| `AddLogger` | Create a new logger configuration |
| `RemoveLogger` | Delete a logger configuration |

## Service Interface

`LoggingService` (`tiferet/interfaces/logging.py`) — abstracts access to logging configurations (formatters, handlers, loggers).

## Relationship to Other Domains

Concrete implementations (e.g., `LoggingYamlRepository`) satisfy this interface.

## Relationships to Other Domains

- **App:** `LoggingContext` is loaded as part of the application interface bootstrap, receiving `LoggingService` via dependency injection. Every application interface can have its own logging configuration.
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

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
