from tiferet import App, TiferetError

# Initialize the Tiferet application with the basic_calc interface.
app = App('basic_calc', app_config='config.yml')

# Define test cases for calculator features.
test_cases = [
    ('calc.add', dict(a=1, b=2), '{} + {} = {}'),
    ('calc.subtract', dict(a=5, b=3), '{} - {} = {}'),
    ('calc.multiply', dict(a=4, b=3), '{} * {} = {}'),
    ('calc.divide', dict(a=8, b=2), '{} / {} = {}'),
    ('calc.divide', dict(a=8, b=0), '{} / {} = {}'),  # Expect error
    ('calc.exp', dict(a=2, b=3), '{} ** {} = {}'),
    ('calc.sqrt', dict(a=16), '√{} = {}'),
]

# Execute each test case, demonstrating calculator features.
for feature_id, data, format_str in test_cases:
    a, b = data.get('a'), data.get('b', None)
    try:
        result = app.run(feature_id, data=data)
        if b is not None:
            print(format_str.format(a, b, result))
        else:
            print(format_str.format(a, result))
    except TiferetError as e:
        print(f'Error: {e.message}')

# Show the most recently executed calculations (persisted via the file loader).
print('\nRecent calculations:')
print(app.run('calc.history', data={}))

# Save, list, and evaluate a variablized formula (persisted via the repository).
print('\nFormulas:')
try:
    saved = app.run('formula.save', data=dict(
        name='Rectangle Area',
        expression='width * height',
    ))
    print(f'Saved {saved.display()}')

    print(app.run('formula.list', data={}))

    area = app.run('formula.eval', data=dict(id='rectangle_area', values=dict(width=3, height=4)))
    print(f'rectangle_area(width=3, height=4) = {area}')
except TiferetError as e:
    print(f'Error: {e.message}')
