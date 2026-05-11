from tiferet import App, TiferetError

# Initialize the Tiferet application with the basic_calc interface.
app = App('basic_calc', app_yaml_file='config.yml')

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
