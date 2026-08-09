# Domain Vision Statement — Tiferet Framework

**Status:** Draft · **Domain:** `tiferet` · **Code:** `tiferet/` · **Branch:** `docs-domain-vision-distillation`

## The bet: an application is a declaration, not a program

Most frameworks make you write your application's shape into code: which class
handles which request, which implementation a piece of business logic talks
to, what happens when something goes wrong. That shape is real, but it is
invisible — the only way to see it is to read every file that expresses it,
and the only way to change it is to edit code and redeploy.

Tiferet takes the opposite bet. An application's entry points, its business
workflows, its error vocabulary, and its logging are all written down as data
— a session here, a workflow there, an error message somewhere else — and the
framework turns that declaration into a running system. The code you do write
is deliberately small and single-purpose: one class that does one thing,
resolved into the workflow by name rather than wired in by hand. Change the
declaration and the application changes; the code underneath does not have to
move.

## What this domain makes real

**Tiferet is the Python framework that turns a declared configuration into a
live application.** Give it a file describing what your app is called, what
services it needs, and what steps each of its features should run, and it
resolves every piece, wires it together, and executes requests against it —
whether those requests arrive from a command line, a script, or (via a thin
adapter) a web request. The framework owns the wiring and the execution loop;
you own only the declaration and the small pieces of logic it points at.

## What we get for it

**Swap an implementation without touching a call site.** A feature step names
a service by id, not by class. Point that id at a different module and class
— or activate a different one per environment via a flag — and every caller
of that service picks up the change automatically. Nothing that consumes the
service has to change.

**One business rule, reachable everywhere.** A workflow declared once runs
identically whether it is triggered from a terminal command, a script, or an
API route, because every entry point funnels through the same execution
engine. There is no separate "business logic for the CLI" and "business logic
for the API" to keep in sync.

**Errors that explain themselves, in the reader's own language.** Every
failure condition an application can name is catalogued up front, with a
message that can be translated per audience. A failure doesn't leak a stack
trace to a user; it resolves to the message the application's author wrote
for exactly that condition.

**Tests that don't need the real world.** Because every workflow step depends
on an abstract contract rather than a concrete class, a test can hand it a
fake and check what it was asked to do — no database, no filesystem, no
network call required to prove the business logic is correct.

**Change that doesn't require a code deploy.** Adding a step to a workflow,
changing which implementation a service resolves to, or adjusting an error's
wording are all edits to the declaration. The classes those edits point at
don't need to change, and often don't need to move at all.

## The core of the work

Every Tiferet application goes through the same four-part journey:

> **Declare** an application, its dependencies, and its workflows → **resolve**
> each declared dependency into a live instance → **execute** a request as an
> ordered set of steps against those instances → **respond** with a result or
> a catalogued, explainable error.

The declaration can describe an arbitrarily large application — new entry
points, new workflows, new dependencies — without the resolution and
execution machinery changing at all. So the design commitment underneath
everything is: **one engine, any number of declared applications.** A single,
fixed request-handling pipeline runs every workflow the same way; what
differs from one Tiferet application to the next is never the engine, only
what has been declared to it. Business logic itself — the actual rule a
workflow step performs — is the one thing Tiferet deliberately leaves to the
application's own code, because that is the one part no framework should be
allowed to declare on a team's behalf.

## What it deliberately does not do

Tiferet does not ship a web server, a database, or a message queue, and it
does not decide which one you use. It owns the composition and execution
layer only; a consumer supplies whatever concrete infrastructure it needs
(an HTTP layer, a real database client) behind the same small set of
contracts every other piece of business logic already depends on.

It does not provide persistence beyond the plain configuration files
(YAML or JSON) it uses for its own declarations — anything past that, an
application brings itself, written the same way as any other piece of
swappable infrastructure.

It does not judge whether a workflow step's business logic is correct. That
logic is the application's own code; Tiferet's job stops at guaranteeing that
the step receives validated input, runs in the declared order, and that
whatever it raises comes back out the other side as a well-formed, catalogued
answer rather than a leaked implementation detail.

---

*Companion document:* `docs/core-domain-distillation.md` — the detailed
walkthrough of the framework's vocabulary, behaviors, and the relationships
between its parts.
