# Repositories in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Kingdom is Keter inverted. Assets emit artifacts to the three above them. Repositories only absorb artifacts from the three above them: `mappers`, `utils`, `interfaces`. Nothing else imports `repos`. They are never exported. That position is **Malkuth**. Persistence is the last node, not a voice that speaks back into the factory. See [architecture.md](architecture.md).

Legal `# ** app` imports: `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders). Illegal: `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.

## Life in the system

A repository is the concrete class that satisfies a Service. `ErrorConfigRepository` implements `ErrorService` and extends `ConfigurationRepository`. Consuming code never imports it. DI configuration names `module_path` and `class_name`. The event depends on `ErrorService`. The kingdom absorbs the promise; it does not advertise itself.

That inversion is the whole philosophy of the package. Keter has no inbound edges and is re-exported as `a`. Malkuth has no outbound edges and is absent from `__init__.py`. If a repo were exported, the factory or the client would start depending on a store. If a repo imported `domain` directly, it would skip Hod’s form-giving and leak a noun that cannot survive a file round-trip. If a repo imported `events`, the last node would start commanding. None of those are granted.

`ConfigurationRepository` (`tiferet/repos/core.py`) is the shared absorption pattern. It knows the file, the encoding, and the default transfer role (`to_data`). It dispatches `_load` / `_save` to `YamlLoader` or `JsonLoader` by extension, and raises `UNSUPPORTED_CONFIG_FILE_TYPE` for anything else. Concrete repos accept `<domain>_config` and forward it as `config_file`. They do not instantiate a loader themselves.

## Absorbing a document

Reads navigate with a `start_node` lambda, then map through the transfer object:

```python
error_data = self._load(
    start_node=lambda data: data.get('errors', {}).get(id)
)
return ErrorConfigObject.model_validate(
    {**error_data, 'id': id}
).map()
```

What the reader just saw: the repo never returns raw YAML. `model_validate` builds the transfer object; `map` builds the aggregate. The event receives form it can mutate. The noun, if needed, is a read of that form.

Writes reverse the motion. `from_model` builds the transfer object. The full file is loaded so sibling sections survive. `to_primitive(self.default_role)` is what hits disk:

```python
error_data = ErrorConfigObject.from_model(error)
full_data = self._load()
full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)
self._save(full_data)
```

Deletes are idempotent. `pop(id, None)` on a missing key is success. The kingdom does not punish a second request to remove what is already gone.

Naming is `<Domain>ConfigRepository`. The `Config` suffix is the shared base, not a claim that every future store will be a YAML file. A SQLite repo would still absorb the same three packages and still not be exported.

Tests are integration tests against real temporary files (`tmp_path`). The value of a repo is the loader-plus-mapper interaction. Mocking that away tests nothing Malkuth is for.

## Structured code design

Use `# *** repos` / `# ** repo:` / `# * init` / `# * method`. Import the Service, the concrete mappers, and `ConfigurationRepository`. No `# ** infra` — third-party I/O flows through the inherited loader. Register via DI. Do not add an `__init__.py` export. Full grammar: [code_style.md](code_style.md). Persistence strategies live in [docs/guides/repos.md](../guides/repos.md).

## In short

- Repos persist and are never exported. That absorption is Malkuth, Keter inverted.
- Legal imports: `interfaces`, `mappers`, `utils`. Never `assets`, `domain`, `events`, `di`, `blueprints`, or `contexts`.
- Implement the Service. Map through transfer objects and aggregates. Do not leak a loader or a path.
- Deletes are idempotent. Reads return aggregates, not raw documents.
- Dependents see the contract, not this package.
