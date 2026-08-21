from app.blueprints.fluent import create_calculator_fluent
from tiferet import TiferetError

# Build the fluent calculator app context.
calc_app = create_calculator_fluent()

# The flagship example: PEMDAS means "5 * 2" binds before folding into "1 + 3".
try:
    result = calc_app.add(1, 3).subtract_from(5).multiply_by(2).result
    print(f'1 + 3 - 5 * 2 = {result}')
except TiferetError as e:
    print(f'Error: {e.message}')

# A second chain demonstrating the starter/continuation pairing.
result = calc_app.add(2, 3).multiply_by(4).subtract_from(1).result
print(f'2 + 3 * 4 - 1 = {result}')

# A third chain exercising add_to/divide_by and a fractional intermediate,
# which is exactly why the arithmetic features' params_schema was widened to float.
result = calc_app.multiply(3, 4).add_to(5).divide_by(2).result
print(f'3 * 4 + 5 / 2 = {result}')

# Each entire chain -- not each pairwise reduction -- is recorded as one
# whole-expression entry via the existing history feature from Chapter 7.
print('\nRecent calculations:')
print(calc_app.run('calc.history', data={}))
