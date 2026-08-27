# Utilities in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Foundation is the capability the rest of the system stands on — physical or computational. Utilities are that foundation. That position is **Yesod**. See [architecture.md](architecture.md).

Legal `# ** app` imports: `interfaces` (including `ServiceError`); `mappers`; sibling utils. Used by `events` (direct or via an interface), `repos` (loaders), and `mappers` only as a runtime visitor callable. Contexts and blueprints do not import this package.

## Two axes, not two kinds

The natural way to describe this package is as two kinds of thing — service-backed physical infrastructure on one side, raw computational helpers on the other. That description is wrong, and it is worth dismantling before anything else, because it invites people to place a util by asking what it is made of.

The two questions are **independent axes**:

1. **Does it carry a Netzach contract?** Two conditions, both required: the computation is genuinely *extensible* — a second implementation is plausible, not hypothetical — and the capability must be *reachable by a feature step*, since only a declared service id can be resolved into a workflow.
2. **Is it physical or computational?** A separate question that does not bear on the first at all.

The off-diagonal cell is occupied, which is what settles it. `LoggingMiddleware`, `CacheMiddleware`, and `TimingMiddleware` are computational rather than physical, and they are service-backed via `MiddlewareService` — precisely because middleware is extensible by nature and has to be wired in by declaration. A computational utility absolutely may be a service. A physical one failing either condition would be imported and called directly.

Notice that the contract decision here is just Netzach's rejection criterion applied one position down. "Perceived, not invented" is the same test: a contract is warranted when the capability genuinely admits a second implementor, and an interface introduced for symmetry is a false abstraction. The reachability condition ties to Chesed, since being reachable means having been declared into a resolution stream. The `utils`/`interfaces` boundary is not a third rule to memorize — it is two existing rules meeting. See [interfaces.md](interfaces.md) and [di.md](di.md).

One honest consequence: **there is no contract-free util in the framework at all.** `FileLoader` itself implements `FileService`, so every file-backed util inherits a contract transitively — `yaml`, `json`, `toml`, `csv`, `csvdict`. `SqliteClient` carries two. The three middlewares carry `MiddlewareService`. The contract-free container is a real affordance with zero in-framework instances, so illustrate it from a dialect rather than presenting it as a framework fact. Stated positively: for every capability the framework placed here, both conditions were satisfied — which is exactly why the taxonomy looked like a kind rather than a test.

## Life in the system

A util encapsulates a repeatable process. File I/O, a SQLite connection, a YAML load, a sort, an embedding call — the domain event should not know which.

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

A new computational util (`EmbeddingClient`) implements an `EmbeddingService` if it must be injectable, or remains a raw class if events will import it directly.

## Uniform in lifecycle, deliberately not uniform in capability

What every util here shares is the contract-and-lifecycle layer: `FileService` via `FileLoader`, `open_file` / `close_file`, context-manager semantics, and one failure mechanism in `ServiceError.raise_for`. That much is genuinely uniform, and a reader who expects uniformity is right about it.

What they do **not** share is the operational surface, which follows each medium's real capability:

- `yaml` and `json` expose `load` and `save`.
- **`TomlLoader` exposes `load` only**, and documents why: writing is not supported because the `tomllib` / `tomli` library only provides parsing.
- `CsvLoader` exposes `read_row` / `read_all` / `write_row` / `write_all`, plus statics.
- `SqliteClient` exposes a connection-and-cursor model with `execute`.

`TomlLoader` is the one to study, because a util that refuses to fake a `save` is Netzach's perceived-not-invented criterion and Gevurah's honest-ontology rule enforced one position down. **A capability that claims more than its substrate can honor is a false abstraction**, and a `save` that raised at runtime would be worse than an absent one. The variety in this package is real; the coherence is in the discipline rather than in the shape.

## The line this position holds is structural, not semantic

A domain object is an image that may be reflected across many mediums, and Yesod's job is keeping that image intact against variation in data structure and storage. Never against variation in domain meaning. Fracture here is structural mangling, not model contamination.

That is the mechanical half of a distinction whose semantic half belongs to Gevurah, and stating both together is what keeps either from being mistaken for the other. See [domain.md](domain.md).

**It cannot see the domain, and that is structural rather than conventional.** `YamlLoader.load` takes `start_node` and `data_factory` as `Callable` and returns `Any`; the module imports only `FileLoader` and `ServiceError`. The domain shape is handed in from outside as a callable, so the position has no means of forming a semantic opinion even if it wanted one. Which is why the legal-but-unused `mappers` import is in character rather than an oversight awaiting correction.

**The failure vocabulary is provably narrow.** Everything this position can fail on is medium: file not found, load error, save error, plus an extension check. There is no error here for data that does not make sense. This is the second position with a demonstrably narrow failure set — after Chesed, whose only legitimate failure is not-found — and in both cases the narrowness is what buys the generality.

**Two-way at the boundary, in a single artifact.** `load` brings a substrate's contents in; `save` puts them out; it is the same class doing both. Every other position is either one-way at the outer boundary or moves data that is already inside: `assets` emits, `repos` absorbs, and `mappers` are bidirectional only within the system's own vocabulary. Do not overstate it — CLI invocation data enters through blueprint parsing, so this is two-way-in-one-artifact rather than the sole point of entry. The useful consequence is that the reflection the descent otherwise seems to lack happens *here*: the import graph is a one-way DAG, but inbound traffic originates at Yesod's `load`, which makes the ninth position the reflecting surface rather than the tenth.

**The contract across every shape is identity preservation across contact with the non-domain.** Round-trip for storage — what is read back is what was written. Pass-through for middleware. Deterministic transform for computation. The middleware docstrings state it outright: the result of `next_fn` is returned unchanged and any exception is re-raised unaltered. That is the framework asserting non-corruption in its own words, with no metaphor vocabulary anywhere near it. `CacheMiddleware` also explicitly declines to import `CacheContext` in order to preserve this boundary.

One thing this position is **not**: an anticorruption layer. An ACL prevents *meaning* from being contaminated; Yesod prevents *data* from being mangled. The ACL composite decomposes across Netzach, Malkuth, Hod, and Tiferet, and Yesod is not among them. See [architecture.md](architecture.md).

Worth saying plainly rather than treating as luck: this may be the position where the metaphor earns the most, because `utils` is the framework's least predictive package name — a grab-bag noun that tells a reader nothing about what may go in it. "Foundation" predicts the boundary discipline above; "utils" predicts nothing at all.

## Current utilities

- `FileLoader` / `File` — `FileService`
- `YamlLoader` / `Yaml` — YAML via PyYAML
- `JsonLoader` / `Json` — JSON with path support
- `TomlLoader` / `Toml` — TOML read only; the substrate does not write
- `CsvLoader` / `Csv`, `CsvDictLoader` / `CsvDict` — list and dict CSV
- `SqliteClient` / `Sqlite` — `SqliteService` + `FileService`; `mode='rw'`, URI and `:memory:`
- `LoggingMiddleware`, `CacheMiddleware`, `TimingMiddleware` — `MiddlewareService`

## Structured code design

Use `# *** utils` / `# ** util:` / `# * method` (and `# * method: <name> (static)`). Tests use `tmp_path` for files and `:memory:` for SQLite. Full grammar: [code_style.md](code_style.md). Cookbooks live under [docs/guides/utils.md](../guides/utils.md).

## In short

- Utils are foundation: physical or computational. That is Yesod.
- Contract-carrying and physical-versus-computational are independent axes, not two kinds. A contract is warranted when the capability is extensible *and* reachable by a feature step.
- The middlewares are the off-diagonal case: computational and service-backed. There is no contract-free util in the framework, so illustrate that affordance from a dialect.
- Uniform in lifecycle, various in capability. `TomlLoader` exposes `load` only, because a capability claiming more than its substrate can honor is a false abstraction.
- The line here is structural, never semantic. Fracture is mangled data, not a contaminated model — and this position cannot form a semantic opinion, since the domain shape arrives as a `Callable`.
- The failure vocabulary is medium-only. No error here means "that does not make sense."
- Two-way in one artifact: `load` in, `save` out. Inbound traffic originates here, which makes the ninth position the reflecting surface rather than the tenth.
- This is not an anticorruption layer. ACL guards meaning; Yesod guards structure.
- Legal imports: `interfaces`, `mappers`, siblings. Not events, domain, repos, di, contexts, or blueprints.
- Raise `ServiceError`. Own resources with a context manager. Offer static one-shots when they help.
- Mappers visit via `Callable`. They do not import this package.
