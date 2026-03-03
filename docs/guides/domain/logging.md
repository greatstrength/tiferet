# Domain – Logging (Observability)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/logging.py`  
**Version:** 2.0.0a2

## Overview

The Logging domain defines **how execution is observed**. It provides a configuration-driven approach to Python's `logging` module, representing formatters, handlers, and loggers as domain objects that can be managed through YAML configuration and domain events — just like any other Tiferet domain concept.

The Logging domain uses a three-model composition: `Formatter` defines how log messages are formatted, `Handler` defines where they go (console, file, etc.), and `Logger` ties them together with a log level and propagation rules. At runtime, `LoggingContext` loads these objects, converts them to a `dictConfig`-compatible dictionary, and produces a live `logging.Logger` instance.

## Domain Objects

### Formatter

Defines the format string and date format for log messages.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `default`, `detailed`) |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Optional description |
| `format` | `str` (required) | Log message format string (e.g., `%(asctime)s - %(name)s - %(message)s`) |
| `datefmt` | `str` | Date format string (e.g., `%Y-%m-%d %H:%M:%S`) |

**Behavior method:**

- `format_config()` — returns a dict with `format` and `datefmt` keys, suitable for `logging.config.dictConfig`.

### Handler

Defines a log destination — where messages are sent and at what level. References a `Formatter` by ID.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `console`, `file`) |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Optional description |
| `module_path` | `str` (required) | Module path for the handler class (e.g., `logging`) |
| `class_name` | `str` (required) | Handler class name (e.g., `StreamHandler`, `FileHandler`) |
| `level` | `str` (required) | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `formatter` | `str` (required) | ID of the `Formatter` to use |
| `stream` | `str` | Stream specification for `StreamHandler` (e.g., `ext://sys.stdout`) |
| `filename` | `str` | File path for `FileHandler` |

**Behavior method:**

- `format_config()` — returns a dict with `class` (combined `module_path.class_name`), `level`, `formatter`, and optional `stream`/`filename` keys.

### Logger

Defines a logger configuration — its level, which handlers it uses, and whether it propagates to parent loggers.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `default`, `app`) |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Optional description |
| `level` | `str` (required) | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `handlers` | `List[str]` (default: `[]`) | IDs of handlers to attach |
| `propagate` | `bool` (default: `False`) | Whether to propagate messages to parent loggers |
| `is_root` | `bool` (default: `False`) | Whether this is the root logger |

**Behavior method:**

- `format_config()` — returns a dict with `level`, `handlers`, and `propagate` keys.

### Three-Model Composition

The logging pipeline is a directed graph:

```
Logger → references Handler IDs → Handler references Formatter ID
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

- **App domain** — Each `AppInterface` specifies a `logger_id` that determines which logger configuration is activated at runtime. When `AppInterfaceContext.run()` is called, it builds the logger before executing the feature.
- **All contexts** — The logger produced by `LoggingContext.build_logger()` is passed to feature execution and used throughout the request lifecycle for debug, info, and error logging.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
