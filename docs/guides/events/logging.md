# Events – Logging Configuration Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/logging.py`  
**Version:** 2.0.0

## Overview

The logging event module provides create, list, and remove operations for the three logging domain objects — `Formatter`, `Handler`, and `Logger`. Every event extends the shared `LoggingEvent` base event (which injects `LoggingService`) and operates through the corresponding aggregate mappers (`FormatterAggregate`, `HandlerAggregate`, `LoggerAggregate`). **Vision:** see the `LoggingEvent` class docstring in `tiferet/events/logging.py` for the value statement this guide distills.

There are no update events — a formatter, handler, or logger configuration is replaced by removing and re-adding it.

## Ubiquitous Language

- **Formatter** — a `Formatter` domain object: a named log-message format string plus optional date format.
- **Handler** — a `Handler` domain object: a logging destination (stream, file, etc.) bound to one `Formatter` by id.
- **Logger** — a `Logger` domain object: a named logger bound to one or more `Handler` ids, assembled into `logging.config.dictConfig` form by `LoggingSettings.format_config()`.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `ListAllLoggingConfigs` | Read (all) | *(none)* | `Tuple[List[Formatter], List[Handler], List[Logger]]` |
| `AddFormatter` | Create | `id`, `name`, `format` | `Formatter` |
| `RemoveFormatter` | Delete | `id` | `str` (ID) |
| `AddHandler` | Create | `id`, `name`, `module_path`, `class_name`, `level`, `formatter` | `Handler` |
| `RemoveHandler` | Delete | `id` | `str` (ID) |
| `AddLogger` | Create | `id`, `name`, `level`, `handlers` | `Logger` |
| `RemoveLogger` | Delete | `id` | `str` (ID) |

## Dependency

<a id="loggingevent"></a>
All events inject a single dependency:

- **`logging_service: LoggingService`** — the service interface for persisting and retrieving logging configuration objects.

## Event Details

### ListAllLoggingConfigs

Retrieves all logging configurations (formatters, handlers, loggers) via a single service call.

**Required:** *(none)*

**Returns:** A tuple of `(List[Formatter], List[Handler], List[Logger])`.

```python
formatters, handlers, loggers = DomainEvent.handle(
    ListAllLoggingConfigs,
    dependencies={'logging_service': logging_service},
)
```

### AddFormatter

Creates a new `Formatter` aggregate and persists it via `LoggingService.save_formatter()`.

**Required:** `id`, `name`, `format`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `description` | `str` | `None` | Optional description of the formatter |
| `datefmt` | `str` | `None` | Optional date format string |

**Returns:** The created `Formatter` instance.

```python
result = DomainEvent.handle(
    AddFormatter,
    dependencies={'logging_service': logging_service},
    id='detailed',
    name='Detailed Formatter',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
```

### RemoveFormatter

Removes a formatter configuration by ID. The operation is idempotent — no error is raised if the formatter does not exist.

**Required:** `id`

**Returns:** `str` — the removed formatter ID.

```python
DomainEvent.handle(
    RemoveFormatter,
    dependencies={'logging_service': logging_service},
    id='old_formatter',
)
```

### AddHandler

Creates a new `Handler` aggregate and persists it via `LoggingService.save_handler()`.

**Required:** `id`, `name`, `module_path`, `class_name`, `level`, `formatter`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `description` | `str` | `None` | Optional description of the handler |
| `stream` | `str` | `None` | Stream specification (e.g., `ext://sys.stdout`) |
| `filename` | `str` | `None` | Filename for file-based handlers |

**Returns:** The created `Handler` instance.

```python
# File handler
result = DomainEvent.handle(
    AddHandler,
    dependencies={'logging_service': logging_service},
    id='file_handler',
    name='File Handler',
    module_path='logging.handlers',
    class_name='RotatingFileHandler',
    level='DEBUG',
    formatter='detailed',
    filename='/var/log/app.log',
)

# Stream handler
result = DomainEvent.handle(
    AddHandler,
    dependencies={'logging_service': logging_service},
    id='console',
    name='Console Handler',
    module_path='logging',
    class_name='StreamHandler',
    level='INFO',
    formatter='simple',
    stream='ext://sys.stdout',
)
```

### RemoveHandler

Removes a handler configuration by ID. The operation is idempotent.

**Required:** `id`

**Returns:** `str` — the removed handler ID.

```python
DomainEvent.handle(
    RemoveHandler,
    dependencies={'logging_service': logging_service},
    id='old_handler',
)
```

### AddLogger

Creates a new `Logger` aggregate and persists it via `LoggingService.save_logger()`.

**Required:** `id`, `name`, `level`, `handlers`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `description` | `str` | `None` | Optional description of the logger |
| `propagate` | `bool` | `True` | Whether to propagate messages to parent loggers |

**Returns:** The created `Logger` instance.

```python
result = DomainEvent.handle(
    AddLogger,
    dependencies={'logging_service': logging_service},
    id='app.database',
    name='Database Logger',
    level='WARNING',
    handlers=['console', 'file_handler'],
    propagate=False,
)
```

### RemoveLogger

Removes a logger configuration by ID. The operation is idempotent.

**Required:** `id`

**Returns:** `str` — the removed logger ID.

```python
DomainEvent.handle(
    RemoveLogger,
    dependencies={'logging_service': logging_service},
    id='old_logger',
)
```

## Boundaries

**Inside this domain:** create/list/remove operations for `Formatter`, `Handler`, and `Logger` configurations.
**Outside this domain:** the declared domain object shapes and `dictConfig` assembly (`LoggingSettings.format_config()` — [docs/guides/domain/logging.md](../domain/logging.md)); building the runtime `logging.Logger` from an assembled config (`LoggingContext` — [docs/guides/contexts.md](../contexts.md)).

## Related Documentation

- [docs/guides/domain/logging.md](../domain/logging.md) — `Formatter`/`Handler`/`Logger`/`LoggingSettings` domain objects
- [docs/guides/contexts.md](../contexts.md) — `LoggingContext`, which builds the runtime logger
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
