# Repos – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/repos/`  
**Version:** 2.0.0

## Overview

Repositories are the concrete data-access layer in Tiferet. Each repository implements a Service interface and inherits the shared `ConfigurationRepository` base, which handles format-specific file I/O for the domain's transfer objects and aggregates. Repositories are highly situational — their functionality is shaped by the specific structural requirements of the configuration format they manage.

This guide covers the cross-cutting strategies and design decisions that apply to all repository modules, rather than any single domain.

## The Service Interface Contract

Every repository implements a Service interface from `tiferet/interfaces/`. The interface defines the abstract CRUD operations; the repository provides the concrete data-utility wiring.

| Repository | Implements | Base |
|---|---|---|
| `AppConfigRepository` | `AppService` | `ConfigurationRepository` |
| `CliConfigRepository` | `CliService` | `ConfigurationRepository` |
| `DIConfigRepository` | `DIService` | `ConfigurationRepository` |
| `ErrorConfigRepository` | `ErrorService` | `ConfigurationRepository` |
| `FeatureConfigRepository` | `FeatureService` | `ConfigurationRepository` |
| `LoggingConfigRepository` | `LoggingService` | `ConfigurationRepository` |

The naming convention is `<Domain>ConfigRepository`. All repositories inherit `ConfigurationRepository`, which resolves the backing loader (`YamlLoader` or `JsonLoader`) from the configuration file extension at runtime.

## No Package Exports

Repositories are **never exported** from `tiferet/repos/__init__.py`. They are resolved at runtime through the DI service registration (`config.yml` or equivalent), which specifies the `module_path` and `class_name` for each concrete implementation. This keeps the dependency graph clean — consuming code depends only on the abstract Service interface, never on a concrete repository.

## Inherited Configuration Foundation

Every repository inherits three instance attributes from the `ConfigurationRepository` base:

```python
# * attribute: config_file
config_file: str

# * attribute: encoding
encoding: str

# * attribute: default_role
default_role: str
```

- **`config_file`** — path to the configuration file (`.yaml`/`.yml` or `.json`).
- **`encoding`** — file encoding (default `'utf-8'`).
- **`default_role`** — the TransferObject serialization role used for writes (`'to_data'`).

The constructor parameter follows the convention `<domain>_config` (e.g., `error_config`, `feature_config`) and is forwarded to the base as `config_file`.

## Reading Patterns

### Start-node navigation

The inherited `_load` helper's `start_node` callback navigates into the configuration structure before returning data to the caller. This isolates the repository from the top-level file layout.

```python
# Single entry by ID.
error_data = self._load(
    start_node=lambda data: data.get('errors').get(id)
)

# Entire section.
interfaces_data = self._load(
    start_node=lambda data: data.get('interfaces', {})
)
```

Repositories use `start_node` for all read operations. The lambda receives the full parsed configuration dict and returns the relevant subsection.

### Data-factory callback

For complex loading that needs to construct multiple transfer objects in a single pass, use the `data_factory` callback:

```python
def data_factory(data):
    registrations = [
        ServiceRegistrationConfigObject.model_validate({**reg_data, 'id': id})
        for id, reg_data in data.get('services', {}).items()
    ] if data.get('services') else []
    consts = data.get('const', {}) if data.get('const') else {}
    return registrations, consts

registrations_data, consts = self._load(
    data_factory=data_factory
)
```

Use `data_factory` when the configuration file contains **multiple sibling sections** that must be returned together (e.g., `services` + `const`, or `formatters` + `handlers` + `loggers`).

### ID derivation from configuration keys

Configuration files store entries as dictionaries keyed by identifier. The ID is not stored inside the value — it is derived from the key and injected during mapping:

```python
return ErrorConfigObject.model_validate(
    {**error_data, 'id': id}   # Key becomes the domain object's ID.
).map()
```

This pattern is universal across all repositories.

## Writing Patterns

### Save: load → update → persist

Every save method follows the same three-step sequence:

1. **Serialize** the domain object via `TransferObject.from_model()` and `to_primitive(default_role)` (which delegates to `model_dump`).
2. **Load the full file** to preserve sibling sections.
3. **Update** the target section with `setdefault` and write back.

```python
# Serialize.
error_data = ErrorConfigObject.from_model(error)

# Load full file.
full_data = self._load()

# Update and persist.
full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)
self._save(full_data)
```

The `setdefault` call ensures the section exists even on a fresh file.

### Delete: load section → pop → persist

Deletes are always **idempotent** — deleting a non-existent entry is a no-op:

```python
# Load the section.
errors_data = self._load(
    start_node=lambda data: data.get('errors', {})
)

# Remove the entry (no error if missing).
errors_data.pop(id, None)

# Load full, update, persist.
full_data = self._load()
full_data['errors'] = errors_data
self._save(full_data)
```

## Grouped YAML Structures

Some domains use **nested grouping** where entries are organized under a parent key. Features are the canonical example — each feature has a composite ID (`group_id.feature_key`) and is stored under its group:

```yaml
features:
  calc:
    add:
      name: Add Number
      steps: [...]
    subtract:
      name: Subtract Number
      steps: [...]
```

The repository splits the composite ID and navigates two levels deep:

```python
group_id, feature_key = id.split('.', 1)
group_data = data.get('features', {}).get(group_id, {})
feature_data = group_data.get(feature_key)
```

Saves use nested `setdefault`:

```python
full_data.setdefault('features', {}).setdefault(group_id, {})[feature_key] = feature_data.to_primitive(self.default_role)
```

Deletes check for empty groups and prune them:

```python
group_data.pop(feature_name, None)
if not group_data and group_id in features_data:
    features_data.pop(group_id, None)
```

## Multi-Section Files

Some YAML files contain **multiple parallel sections** that represent different entity types. Two patterns handle this:

### Tuple return (container / DI)

The repository's `list_all` returns a tuple of section results:

```python
def list_all(self) -> Tuple[List[ServiceRegistration], Dict[str, str]]:
    # data_factory returns (registrations_list, constants_dict)
```

Each section is parsed independently within the `data_factory`.

### Composite transfer object (logging)

The logging repository uses `LoggingSettingsConfigObject` — a transfer object that composes `FormatterConfigObject`, `HandlerConfigObject`, and `LoggerConfigObject` into a single object representing the entire file:

```python
data = self._load(
    data_factory=lambda d: LoggingSettingsConfigObject.hydrate(**d),
    start_node=lambda d: d.get('logging', {})
)
return (
    [f.map() for f in data.formatters.values()],
    [h.map() for h in data.handlers.values()],
    [l.map() for l in data.loggers.values()],
)
```

Use the composite pattern when the sections are tightly coupled and always loaded together. Use the tuple pattern when sections are logically independent.

## Testing Repositories

Repository tests use `pytest` with temporary YAML files created via `tmp_path`:

```python
@pytest.fixture
def config_file(tmp_path) -> str:
    file_path = tmp_path / 'test_config.yaml'
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(SAMPLE_DATA, f)
    return str(file_path)
```

Standard test cases cover:

- **exists** — positive and negative lookups.
- **get** — retrieval by ID; `None` for missing entries.
- **list / list_all** — full enumeration with count and field assertions.
- **save** — round-trip: save then retrieve and verify fields.
- **delete** — delete then confirm `exists` returns `False`.
- **save_constants** (where applicable) — merge semantics and overwrite behavior.

Tests operate against real temporary files, not mocks, because the repository's value is in the specific interaction between the utility and the transfer objects.

## Creating a New Repository

1. **Define the Service interface** in `tiferet/interfaces/<domain>.py` with abstract CRUD methods.
2. **Implement the repository** in `tiferet/repos/<domain>.py`:
   - Extend the Service interface together with `ConfigurationRepository`.
   - Forward the `<domain>_config` path to the `ConfigurationRepository` base in `__init__`.
   - Implement each method using the read/write patterns above.
3. **Write tests** in `tests/repos/test_<domain>.py` with sample configuration data and `tmp_path` fixtures.
4. **Register via DI** — add the repository to the DI configuration file with `module_path` and `class_name`. No `__init__.py` export needed.

## Related Documentation

- [docs/core/repos.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/repos.md) — Repository base patterns and structured code design
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
- [docs/guides/mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/mappers.md) — Aggregate and TransferObject patterns
- [docs/guides/utils/yaml.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/utils/yaml.md) — YamlLoader utility guide
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
