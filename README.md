# Tiferet – Domain-Driven Design, beautifully balanced

[![PyPI](https://img.shields.io/pypi/v/tiferet?style=flat-square&logo=python&logoColor=white&color=3775A9)](https://pypi.org/project/tiferet/)
[![Python](https://img.shields.io/pypi/pyversions/tiferet?style=flat-square&logo=python&logoColor=white&color=3775A9)](https://pypi.org/project/tiferet/)
[![License](https://img.shields.io/github/license/greatstrength/tiferet?style=flat-square)](LICENSE)

**Tiferet** is a Python framework that brings **Domain-Driven Design** into focus with elegance and clarity.

Inspired by the Kabbalistic principle of harmony and beauty in balance, Tiferet helps you turn complex business logic into maintainable, configuration-driven applications — where purpose, structure, and execution feel naturally aligned.

### At a glance
- Builders-first app entry point via `build_app` (exported as `App`)  
- Domain events as the core unit of behavior  
- YAML for features, workflows, dependency injection, errors, CLI commands  
- Clean layering: domain objects • aggregates • transfer objects • services  
- Structured, multilingual errors built-in  
- Easy to extend to CLI, web, scripts, TUI, …
Current status: **2.0.0a10** (pre-release – actively evolving toward stable v2)

## Quick Start – Add two numbers in ~3 minutes

```bash
# 1. Set up environment
python3 -m venv tiferet-demo && source tiferet-demo/bin/activate
pip install tiferet
```

Create these files in your project folder:

**demo.py**
```python
from tiferet import App
app = App().load_app_service(
    app_yaml_file="config.yml"
)                               # App is the build_app alias

result = app.run(
    interface_id="basic_calc",
    feature_id="calc.add",
    data={"a": 19, "b": 23}
)

print(f"19 + 23 = {result}")    # → 42
```
**config.yml**
```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Basic calculator interface

services:
  add_number_event:
    module_path: app.events.calc
    class_name: AddNumber

features:
  calc:
    add:
      name: Add Numbers
      commands:
        - service_id: add_number_event
```

**app/events/calc.py**  
(the domain event itself – very minimal)

```python
from tiferet.events import DomainEvent

class AddNumber(DomainEvent):
    def execute(self, a: int, b: int, **kwargs) -> int:
        return a + b
```

Run:

```bash
python demo.py
```

You should see:

```
19 + 23 = 42
```

→ Want a full calculator (add, subtract, multiply, divide, sqrt, …) with CLI, validation and proper error handling?  
→ Continue with the **[step-by-step Calculator Tutorial →](docs/tutorial/basic_calculator/index.md)**

## Why Tiferet?

- **Configuration as code** — features, DI, errors, CLI all live in YAML  
- **Domain logic stays pure** — focused events & aggregates  
- **Infrastructure is injectable** — file/db/utils behind clean service contracts  
- **Built for evolution** — today CLI, tomorrow FastAPI or TUI  
- **Strong testability** — events are easy to invoke in isolation

## Documentation & Guides

**Core architecture**  
- [Code Style & Artifact Comments](docs/core/code_style.md)  
- [Builders (build_app)](docs/core/blueprints.md)  
- [Domain Objects](docs/core/domain.md)  
- [Domain Events](docs/core/events.md)  
- [Aggregates & Transfer Objects (Mappers)](docs/core/mappers.md)  
- [Service Interfaces](docs/core/interfaces.md)  
- [Dependency Injection (ServiceProvider)](docs/core/di.md)  
- [Repositories](docs/core/repos.md)  
- [Utilities (File/Yaml/Json/Csv/Sqlite)](docs/core/utils.md)

### Practical Guides 
**Domain Guides**  
- [Application Management](docs/guides/domain/app.md)  
- [Dependency Injection](docs/guides/domain/di.md)  
- [Feature Workflows](docs/guides/domain/feature.md)  
- [Error Handling](docs/guides/domain/error.md)  
- [CLI Integration](docs/guides/domain/cli.md)  
- [Logging](docs/guides/domain/logging.md)

**Event Guides**  
- [Application Events](docs/guides/events/app.md)  
- [Dependency Injection Events](docs/guides/events/di.md)  
- [Feature Events](docs/guides/events/feature.md)  
- [Error Events](docs/guides/events/error.md)  
- [CLI Integration Events](docs/guides/events/cli.md)  
- [Logging Events](docs/guides/events/logging.md)  
- [SQLite Events](docs/guides/events/sqlite.md)

**Utility Guides**  
- [File Loader](docs/guides/utils/file.md)  
- [YAML Loader](docs/guides/utils/yaml.md)  
- [JSON Loader](docs/guides/utils/json.md)  
- [CSV Loader](docs/guides/utils/csv.md)  
- [Sqlite Connector](docs/guides/utils/sqlite.md)

**Other Component Guides**  
- [Interfaces](docs/guides/interfaces.md)  
- [Mappers (Aggregates & Transfer Objects)](docs/guides/mappers.md)  
- [Repositories](docs/guides/repos.md)

**Tutorial**  
→ [Build a complete Calculator (events + CLI + configs)](docs/tutorial/basic_calculator/index.md)

## Contributing

We welcome bug reports, documentation improvements, feature ideas, and early adopters.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow (issues → TRD → feature branch → PR).

Questions, feedback, or just want to say hi?  
Open an issue or reach out via email: andrew@greatstrength.me

Let's build software that feels as good as it works.