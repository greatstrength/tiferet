# Basic Calculator Tutorial

Hey there! 👋

Welcome to the hands-on guide where we're going to build a clean, elegant calculator using **Tiferet** — the framework that turns domain-driven design into something that actually feels good to work with.

By the time we're done, you'll have:
- Add, subtract, multiply, divide, and square root operations
- Smart input validation with nice error messages
- A reusable utility class for number verification (in `app/utils/`)
- Everything wired together through simple YAML configuration files
- Two ways to use it: a quick script for testing and a proper command-line interface

And best of all — each step is small, satisfying, and shows real progress.

### What we'll build (final project layout)

```
basic-calculator/
├── basic_calc.py               # quick script runner for testing
├── calc_cli.py                 # full-featured command-line calculator
└── app/
    ├── configs/                # where all the YAML magic lives
    │   ├── app.yml
    │   ├── container.yml
    │   ├── error.yml
    │   ├── feature.yml
    │   └── cli.yml             # only needed for the CLI
    ├── events/
    │   ├── __init__.py
    │   └── calc.py             # our arithmetic domain events
    └── utils/
        ├── __init__.py
        └── calc.py             # reusable validation helpers
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
   Fire up `basic_calc.py` and watch it work (success cases + graceful errors).

6. **[CLI Interface & Commands](06-cli-interface.md)**  
   Add the command-line polish so you can type `calc add 19 23` like a pro.

This tutorial is designed to feel like we're building together — short steps, quick wins, and no walls of text.

Ready to get started?  
→ Jump to **[Step 1: Setup & Entry Points](01-setup-and-entry-points.md)**

See you there!
