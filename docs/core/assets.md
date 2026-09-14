# Assets in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Decision support begins here. Composition has to begin from something that does not depend on the composition. `assets` is that package: shared primitives — exceptions, named error codes, and bootstrap catalogs — with no inbound framework edges.

It does not execute a feature, mutate a noun, or open a file. It declares concepts of the app that must exist before the app exists, so the app may exist. A blueprint needs names to seed. A session needs errors to raise. A dialect needs a Bounded Context to enter. Catalogs and constants are the emission. The package does not become runtime. See [architecture.md](architecture.md).

Legal `# ** app` imports: none. The package imports only standard-library and third-party primitives. An asset that required a domain object or a service would already be a runtime collaborator rather than a prerequisite.

The package uses the standard code-style components and has no unique component of its own. Artifact grammar is [code_style.md](code_style.md). Catalog construction is [docs/guides/assets.md](../guides/assets.md).

## Bounded Context before use

Acyclicity is the bootstrap constraint. `assets` has no framework imports because its primary purpose is to describe the structure and prerequisites of the application Bounded Context before that context is used. A package that imported framework behavior could not serve as the origin of composition.

That description is the catalog. Default errors, services, constants, features, commands, and logging settings are declared prerequisites of a running session. A blueprint seeds those catalogs into the cache. A session may override what a catalog declares. The catalog itself is not mutated. Mutable state belongs to a domain noun.

The catalogs are data, not the nouns they name. Factories in this package assemble structured definitions — identifiers, names, messages, service coordinates, feature steps — so entries do not diverge into unstructured inline dictionaries. Reconstitution into domain objects happens outside this package, during cache seeding. The same principle holds across every catalog in the package, in the framework and in a dialect.

A consumer's assets are the same pattern, not a second one. They declare that dialect's Bounded Context — its errors, resolvable operators, exposed features — before any `execute` exists. Framework catalogs and dialect catalogs differ in content, not in job.

## Emission

Assets hold no operational behavior. Their catalogs are loaded during composition and referenced on every runtime path, but the package does not run a feature, change domain state, or touch a substrate. The contents are not renegotiated while the application runs.

Emission is narrow. `assets` emits to `blueprints`, `contexts`, and `events`. Blueprints seed catalogs into the cache. Contexts and events raise named errors through `a.<submodule>` (`a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`).

Core assets may be used by other assets. They do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`. Where those packages need a catalogued value, it arrives as data assembled by a blueprint — reverse dependency across an import-law gap, the same shape that lets `di` resolve what these catalogs named without importing this package.

`TiferetError` is a standalone class, not a domain object. `error_code` and `kwargs` are what an event's `raise_error` and a context's error handler both understand. Assets name the failure. They do not present it. Localized formatting belongs to the domain noun after the runtime handler hub has loaded the catalogued `Error`.

## Importing `a`

The public binding is the root alias `a`. Current releases export it from the framework root (`from tiferet import a`) and import it downward into the packages that consume catalogs and named errors (`from .. import a`, or `from .. import assets as a`). The package is imported whole and referenced through differentiated members.

Namespaced access keeps one package boundary and distinct catalogs. It is not an undifferentiated constants module. New public symbols are surfaced on that binding. New concerns that need a noun, a contract, or a unit of work do not belong in this package.

## In short

- Decision support. Composition begins from primitives that do not depend on the composition.
- `assets` declares concepts that must exist before the app exists so the app may exist.
- Acyclic: no inbound framework edges. Primary purpose is bootstrap — the Bounded Context's structure and prerequisites, declared before use.
- Emits catalogs and constants. Does not become runtime.
- Standard code-style components only. No unique component.
- Emits to `blueprints`, `contexts`, and `events`. Other packages receive catalogued values as data through composition.
- Imported whole as `a` from the framework root and referenced as `a.error`, `a.app`, `a.feat`, `a.cli`, `a.logging`.
- Framework and dialect catalogs are the same pattern: they describe a Bounded Context before behavior exists.
- If a concern needs a noun, a contract, or a unit of work, it is not an asset.
