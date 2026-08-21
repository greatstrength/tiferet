from app.blueprints.calc import create_calculator_cli

if __name__ == '__main__':
    # Uses the calculator's own CLI blueprint (not the generic CLI(...))
    # so the arithmetic bounded-context defaults are available here too.
    create_calculator_cli()
