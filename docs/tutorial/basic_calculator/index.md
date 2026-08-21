# Basic Calculator Tutorial

Hey there! 👋

Welcome to the hands-on guide where we're going to build a clean, elegant calculator using **Tiferet** — the framework that turns domain-driven design into something that actually feels good to work with.

By the time we're done, you'll have:
- Add, subtract, multiply, divide, and square root operations
- Smart input validation with nice error messages
- A reusable utility class for number verification (in `app/utils/`)
- Everything wired together through simple YAML configuration files
- Three ways to use it: a plain client, a command-line interface, and a fluent chain
- Persist your most recently executed calculations and formulas to a file
- Save and re-evaluate named, variablized formulas
- The arithmetic operators themselves shipped as a calculator-owned bounded context
- A fluent, chainable calculator client that evaluates PEMDAS-aware expressions

And best of all — each step is small, satisfying, and shows real progress.

### What we'll build (final project layout)

```
basic_calculator/
├── calc_client.py         # plain, non-fluent client entry point (Step 9)
├── calc_cli.py            # command-line calculator entry point (Step 10)
├── calc_fluent.py         # fluent, PEMDAS-aware calculator client (Step 11)
├── config.yml             # consolidated configuration
├── formulas.yml           # saved formulas store (Step 8)
├── history.json           # recent calculations, generated at runtime (Step 7)
└── app/
    ├── assets/            # operator constants and default catalogs (Step 10)
    ├── domain/            # Formula + Expression domain models (Steps 8, 11)
    ├── events/            # arithmetic, history, formula, and expression events
    ├── interfaces/        # FormulaService contract (Step 8)
    ├── mappers/           # Formula aggregate + config object (Step 8)
    ├── repos/             # FormulaConfigRepository (Step 8)
    ├── contexts/          # CalculatorAppContext + CalculatorFluentContext (Steps 9, 11)
    └── blueprints/        # create_calculator_app/_cli/_fluent (Steps 9-11)
```

### The step-by-step path

1. **[Setup & Entry Points](01-setup-and-entry-points.md)**  
   Get your environment ready and see what the finished calculator looks like in action — the "wow" moment first.

2. **[Domain Events – Initial Version](02-domain-events.md)**  
   Write the core math operations as simple, pure domain events.

3. **[Utilities & Refined Events](03-utils-and-refined-events.md)**  
   Introduce a helpful utility for number validation, then clean up the events to use it.

4. **[Configurations](04-configurations.md)**  
   Dive into each YAML file — what it does, why it's there, how the pieces connect.

5. **[Running the Script Runner](05-running-the-script.md)**  
   Fire up `calc_client.py` and watch it work (success cases + graceful errors).

6. **[CLI Interface & Commands](06-cli-interface.md)**  
   Add the command-line polish so you can type `calc add 19 23` like a pro.

7. **[Persisting Recent Formulas](07-persisting-recent-formulas.md)**  
   Use the file loader to remember the most recently executed calculations.

8. **[Saving & Variablizing Formulas](08-saving-and-variablizing-formulas.md)**  
   Save reusable, named formulas with a domain model and repository, then evaluate them.

9. **[The Calculator as a Client](09-the-calculator-as-a-client.md)**  
   Give the calculator its own `AppSessionContext` subclass and blueprint, and turn history recording into a session-level concern instead of a per-feature step.

10. **[The Arithmetic Operators as a Bounded Context](10-the-arithmetic-operators-as-a-bounded-context.md)**  
    Move the arithmetic operators out of `config.yml` into calculator-owned defaults that ship regardless of configuration.

11. **[The Fluent Calculator Context](11-the-fluent-calculator-context.md)**  
    Close the loop with a chainable calculator client that logs a whole expression before resolving it in a single run, PEMDAS and all.

This tutorial is designed to feel like we're building together — short steps, quick wins, and no walls of text.

Ready to get started?  
→ Jump to **[Step 1: Setup & Entry Points](01-setup-and-entry-points.md)**

See you there!
