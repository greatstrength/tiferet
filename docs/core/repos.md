# Repositories in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Kingdom is Keter inverted, and the cardinality is exact. `assets` emits to exactly three positions; repositories absorb from exactly three — `interfaces`, `mappers`, `utils`. Nothing else imports `repos`. They are never exported. That position is **Malkuth**. Persistence is the last node, not a voice that speaks back into the factory. See [architecture.md](architecture.md).

Legal `# ** app` imports: `interfaces` (the Service being implemented, and `ServiceError`); `mappers` (transfer objects and aggregates); `utils` (loaders). Illegal: `assets`, `domain` (use a mapper), `events`, `di`, `blueprints`, `contexts`.

## Life in the system

A repository is the concrete class that satisfies a Service. `ErrorConfigRepository` implements `ErrorService` and extends `ConfigurationRepository`. Consuming code never imports it. DI configuration names `module_path` and `class_name`. The event depends on `ErrorService`. The kingdom absorbs the promise; it does not advertise itself.

That inversion is the whole philosophy of the package. Keter has no inbound edges and is re-exported as `a`. Malkuth has no outbound edges and is absent from `__init__.py`. If a repo were exported, the factory or the client would start depending on a store. If a repo imported `domain` directly, it would skip Hod’s form-giving and leak a noun that cannot survive a file round-trip. If a repo imported `events`, the last node would start commanding. None of those are granted.

`ConfigurationRepository` (`tiferet/repos/core.py`) is the shared absorption pattern. It knows the file, the encoding, and the default transfer role (`to_data`). It dispatches `_load` / `_save` to `YamlLoader` or `JsonLoader` by extension, and raises `UNSUPPORTED_CONFIG_FILE_TYPE` for anything else. Concrete repos accept `<domain>_config` and forward it as `config_file`. They do not instantiate a loader themselves.

## Highest in dependency, last in descent

The imports-only, never-exported rule sounds like a restriction until you notice which ordering it belongs to.

The layer *depended upon* is the lower one. So a pure sink — a package that imports three others and is imported by none — sits at the **top** of a dependency stack while being the last position in the descent. That is not a paradox; it is the two orderings running opposite ways, and this is the position where the inversion is most extreme. See [architecture.md](architecture.md).

Worth noting that the word *repository* does not predict this at all. Plenty of architectures export repositories freely and let application code import them directly. The rule here comes from the position, not from the noun.

## The two clauses are one structure

This position may import neither `domain` nor `contexts`, and the two prohibitions are usually read as separate housekeeping. They are one structure stated from both ends, and together they are the strongest thing this chapter has to say.

A repository produces state whose final realized form is a domain type it is **forbidden to name**, delivered to a seat it **cannot see**. It hands its product off through mappers and interfaces without ever learning the destination. Nothing stands above it in dependency — and yet it possesses nothing, because its product comes to rest somewhere else entirely.

Neither clause is complete without the other. Take away the `domain` prohibition and the position would be naming what it makes; take away the `contexts` prohibition and it would be addressing where its product goes. Together they describe a tier that produces the most concrete thing in the system and keeps none of it.

**The seat is a terminus, which makes it a lifecycle claim rather than a connection claim.** No import edge is inferred from it, and none exists. But the binding at the far end is structural rather than incidental: `BaseContext` declares `domain_type` at class level, `ContextMeta` registers the mapping from domain type to context class, and `from_domain` is type-driven. Domain types are constitutive of contexts, so a repository's product really does come to rest in a context — by way of a type it never mentions.

### The system learns its own shape from here

The cleanest evidence is the framework's own bootstrap, which runs repository to context: a configuration repository reads the config file, `GetAppSession` produces the `AppSession` domain object, and a blueprint realizes it as `AppSessionContext`.

That is the terminus claim in code, and it is distinctive to this position rather than the generic observation that returned values eventually reach a context. **The application's own definition of itself enters the system through Malkuth.**

### Declared forms are deployed here

Hod declares the forms; Malkuth deploys them. A repository performs transfer-object and aggregate mapping inside its interface methods, which is where the declarations from one position up actually do their work.

That is also why `repos` must reach `domain` through a mapper — the troops, not the general. The rule is derivable from the relation rather than memorized as a line in a table. See [mappers.md](mappers.md).

### This position is Potential, not Operations

A tempting inference: `ConfigurationRepository` is *composed of* a loader, so surely composition is an operation performed upon a capability, which would put this tier on the Operations side of Evans' boundary.

That inference runs backwards. Evans defines Potential as the resources of an organization **and the way those resources are organized** — so a repository composed of a loader is one resource arranged from another. That is Potential's own internal structure, not an act performed upon it. The decisive test is his own question: is a repository what is being *done*, or what *enables* doing? It enables. It is fixed capital investment in his exact sense, built once and underwriting all subsequent domain work, and "contracts with vendors also define potentials" covers the Service it implements besides.

Stated plainly: the ability to support a new bounded context rests on the means to support it. An idea with no means stays an idea. This position is the means that legitimize the operation.

**Which relocates Operations upward, and the one-way rule then holds exactly.** If the means are here, Operations is the feature loop — `events` doing the work, `contexts` sequencing it. Evans requires that Operations objects reference or be composed of Potential objects while Potential never references Operations, and the import law delivers precisely that: `events` reach `utils` and receive repositories through Netzach contracts, while `utils` and `repos` may not import `events` at all. The rule is satisfied on every edge, in the correct direction.

The ninth-to-tenth edge is an ordering *within* Potential rather than a crossing out of it: raw capability becoming organized means, since Evans places both the resources and their arrangement on the same side. The relation is real and still one-way. It is the layer boundary that sits elsewhere — at the veil, above both.

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

- Repos persist and are never exported. That absorption is Malkuth, Keter inverted, and the cardinality is exact on both ends.
- Highest in dependency, last in descent. A pure sink tops a dependency stack, which is the two orderings running opposite ways.
- The `domain` and `contexts` prohibitions are one structure: this tier produces a form it may not name, for a seat it cannot see, and keeps none of it.
- The seat is a terminus, and the binding is structural — `domain_type`, `ContextMeta`, and `from_domain` make domain types constitutive of contexts.
- The application's own definition of itself enters here: config repository → `GetAppSession` → `AppSessionContext`.
- Hod declares the forms; Malkuth deploys them. That is why `repos` reaches `domain` only through a mapper.
- This position is Potential, not Operations. It is what enables doing, not what is done — which puts Operations at the feature loop and satisfies Evans' one-way rule on every edge.
- Legal imports: `interfaces`, `mappers`, `utils`. Never `assets`, `domain`, `events`, `di`, `blueprints`, or `contexts`.
- Implement the Service. Map through transfer objects and aggregates. Do not leak a loader or a path.
- Deletes are idempotent. Reads return aggregates, not raw documents.
- Dependents see the contract, not this package.
