# Utilities in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Foundation is the capability the rest of the system stands on — physical or computational. Utilities are that foundation. That position is **Yesod**. Two shapes share the package: a Service-backed util that implements an interface and is therefore DI-injectable, and a raw computational container that events may import and call directly. See [architecture.md](architecture.md).

Legal `# ** app` imports: `interfaces` (including `ServiceError`); `mappers`; sibling utils. Used by `events` (direct or via an interface), `repos` (loaders), and `mappers` only as a runtime visitor callable. Contexts and blueprints do not import this package.

## Life in the system

A util encapsulates a repeatable process. File I/O, a SQLite connection, a YAML load, a sort, an embedding call — the domain event should not know which. When the process must be swapped through DI, the util implements a Netzach contract (`FileService`, `SqliteService`, `MiddlewareService`). When it has no external collaborator, it can remain a raw container. Both are Yesod. Implementing a Service is required only for the first shape.

Physical infrastructure usually owns a resource and therefore implements the context-manager protocol. `FileLoader` opens and closes a stream. `SqliteClient` commits on success and rolls back on exception. Computational infrastructure is often stateless and needs no `__enter__`. The pattern of the class does not change: artifact comments, structured errors, a focused job.

Errors are `ServiceError.raise_for(self, ...)`, not raw exceptions and not `TiferetError` imported from assets. Yesod talks in contract failures. The event above it turns those into named domain outcomes when the production requires it.

Repos are the primary consumers of loaders. `FeatureConfigRepository` uses `YamlLoader` through `ConfigurationRepository`; it does not reimplement `safe_load`. Events consume Service-backed utils through the injected interface, and raw utils by import. Mappers never import this package. If an aggregate needs a visitor, it takes a `Callable` and the util arrives at runtime.

`LoggingMiddleware` and `TimingMiddleware` are Yesod wrapped around Tiferet: they implement `MiddlewareService` and take a `logger_id`. They do not become events.

## The FileLoader base

`FileLoader` implements `FileService` and is the parent of the file-shaped utils. Path is stored as `pathlib.Path`. Mode and encoding are verified. `verify_file` adapts existence checks to read versus write. `__enter__` opens; `__exit__` closes. Double-open is guarded.

```python
# *** utils

# ** util: file_loader
class FileLoader(FileService):
    '''
    Base utility for low-level file stream operations.
    '''

    # * attribute: path
    path: Path

    # * init
    def __init__(self, path, mode='r', encoding=None, newline=None, **kwargs):
        ...

    # * method: open_file
    def open_file(self):
        ...

    # * method: __enter__
    def __enter__(self):
        ...
```

What the reader just saw: the util *is* the file contract. Format loaders (`YamlLoader`, `JsonLoader`, `CsvLoader`, `CsvDictLoader`) extend this and add `load` / `save`. `SqliteClient` extends it, implements `SqliteService` as well, and returns `self` from `__enter__` because the resource is a connection, not a stream.

One-shot static helpers (`CsvLoader.load_rows`, `JsonLoader.parse_json_path`) exist so a caller who does not need a long-lived instance is not forced to manage one. They are still Yesod, not events.

A new physical util (a `TomlLoader`) extends `FileLoader`, enforces its extension, and raises `ServiceError`. A new computational util (`EmbeddingClient`) implements an `EmbeddingService` if it must be injectable, or remains a raw class if events will import it directly.

## Current utilities

- `FileLoader` / `File` — `FileService`
- `YamlLoader` / `Yaml` — YAML via PyYAML
- `JsonLoader` / `Json` — JSON with path support
- `CsvLoader` / `Csv`, `CsvDictLoader` / `CsvDict` — list and dict CSV
- `SqliteClient` / `Sqlite` — `SqliteService` + `FileService`; `mode='rw'`, URI and `:memory:`
- `LoggingMiddleware`, `TimingMiddleware` — `MiddlewareService`

## Structured code design

Use `# *** utils` / `# ** util:` / `# * method` (and `# * method: <name> (static)`). Tests use `tmp_path` for files and `:memory:` for SQLite. Full grammar: [code_style.md](code_style.md). Cookbooks live under [docs/guides/utils.md](../guides/utils.md).

## In short

- Utils are foundation: physical or computational. That is Yesod.
- Two shapes: Service-backed (injectable) or raw (imported by events). Service implementation is optional.
- Legal imports: `interfaces`, `mappers`, siblings. Not events, domain, repos, di, contexts, or blueprints.
- Raise `ServiceError`. Own resources with a context manager. Offer static one-shots when they help.
- Mappers visit via `Callable`. They do not import this package.
