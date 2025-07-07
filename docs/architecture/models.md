# Tiferet Models Documentation

This document serves as an educational guide for human and AI developers to understand, define, and use domain models in the Tiferet framework, a modular, configuration-driven platform inspired by Domain-Driven Design (DDD) and the Kabbalistic principle of beauty in balance. Using the `tiferet-calculator-app`, it explains domain models, their static and functional artifacts, the distinction between entities and value objects, and how to define, instantiate, and test models, with practical code examples including artifact comments and proper attribute spacing.

## What Are Domain Models?

Domain models in Tiferet are immutable objects that encapsulate the data and logic of an application’s domain, such as numeric values or calculations in the `tiferet-calculator-app`. Built on `tiferet.models.ValueObject` or `tiferet.models.Entity` (from `tiferet/models/settings.py`), they ensure immutability, type safety, and validation using Tiferet types (e.g., `StringType`, `ModelType`). Models form the foundation of Tiferet’s DDD approach, balancing simplicity and robustness to represent domain concepts like calculator inputs or results.

### Entities vs. Value Objects

- **Entities**:

  - **Definition**: Models with a unique identity, defined by a required `id` attribute (e.g., `StringType(required=True)`). They represent domain objects where tracking individual instances matters, such as a specific calculation instance for auditing.
  - **Characteristics**: Inherit from `Entity`, extending `ModelObject` with a mandatory `id`. Immutable per instance but trackable across operations.
  - **Example** (in `app/models/calc.py`):

    ```python
    # ** model: calculation
    class Calculation(Entity):
        '''
        An entity representing a calculator operation with inputs and result.
        '''
        
        # * attribute: id
        id = StringType(
            required=True,
            default=str(uuid4()),
            metadata=dict(
                description='Unique identifier for the calculation.'
            )
        )
        
        # * attribute: a_num
        a_num = ModelType(
            Number,
            required=True,
            metadata=dict(
                description='First input number.'
            )
        )
        
        # * attribute: b_num
        b_num = ModelType(
            Number,
            required=True,
            metadata=dict(
                description='Second input number.'
            )
        )
        
        # * attribute: result
        result = StringType(
            default='',
            metadata=dict(
                description='Result as a string.'
            )
        )
    
        # * method: set_result
        def set_result(self, result: str = None)
            '''
            Sets the result of the calculation.
            '''

            # Set the result as a string if not None.
            if result:
                self.result = str(result)
            
            # Set the default value if None.
            else:
                self.result = ''
            
        # * method: add
        def add(self):
            '''
            Adds a_num to b_num.
            '''
            # Add the numbers.
            result = self.a_num.format() + self.b_num.format()
            
            # Set the result.
            self.set_result(result)
        
        # * method: subtract
        def subtract(self):
            '''
            Subtracts b_num from a_num.
            '''
            # Subtract the numbers.
            result = self.a_num.format() - self.b_num.format()
            
            # Set the result.
            self.set_result(result)
        
        # * method: multiply
        def multiply(self):
            '''
            Multiplies a_num by b_num.
            '''
            # Multiply the numbers.
            result = self.a_num.format() * self.b_num.format()
            
            # Set the result.
            self.set_result(result)
        
        # * method: exponentiate
        def exponentiate(self):
            '''
            Raises a_num to the power of b_num.
            '''
            # Exponentiate the numbers.
            result = self.a_num.format() ** self.b_num.format()
            
            # Set the result.
            self.set_result(result)
    ```

- **Value Objects**:

  - **Definition**: Models without unique identity, defined by their attribute values. Two value objects with identical attributes are interchangeable.
  - **Characteristics**: Inherit from `ValueObject`, focusing on data and behavior (e.g., formatting numbers). Fully immutable and lack an `id`.
  - **Example** (in `app/models/calc.py`):

    ```python
    # ** model: number
    class Number(ValueObject):
        '''
        A value object representing a numerical value in the calculator domain.
        '''
        
        # * attribute: value
        value = StringType(
            required=True,
            regex=r'^-?\d*\.?\d*$',
            metadata=dict(
                description='A string representing an integer or float (e.g., "123", "-123.45").'
            )
        )
        
        # * method: is_float
        def is_float(self) -> bool:
            '''
            Check if the value is formatted as a float.
            :return: True if the value contains a decimal point and valid digits, False otherwise.
            '''
            return '.' in self.value and self.value.strip('-.').replace('.', '').isdigit()
        
        # * method: format
        def format(self) -> int | float:
            '''
            Convert the string value to an integer or float.
            :return: An integer if whole number, otherwise a float.
            '''
            if self.is_float():
                return float(self.value)
            return int(self.value)
    
        # * method: set_result
        def set_result(self, result: str = None)
            '''
            Sets the result of the calculation.
            '''

            # Set the result as a string if not None.
            if result:
                self.result = str(result)
            
            # Set the default value if None.
            else:
                self.result = ''
    ```

## Static and Functional Artifacts

Domain models consist of static attributes and functional methods, leveraging types from `tiferet/models/settings.py`:

- **Static Artifacts (Attributes)**:

  - **Definition**: Attributes use Tiferet types (e.g., `StringType`, `ModelType`) with validation rules like `required=True`, regex, or choices. For example, `StringType(regex=r'^-?\d*\.?\d*$')` ensures valid numeric strings.
  - **Purpose**: Represent core properties, such as `value` in `Number` or `a_num: ModelType(Number)` in `Calculation`. Metadata (e.g., `description`) aids documentation.
  - **Example** (from `Calculation` in `app/models/calc.py`):

    ```python
    # * attribute: id
    id = StringType(
        required=True,
        default=str(uuid4()),
        metadata=dict(
            description='Unique identifier for the calculation.'
        )
    )
    
    # * attribute: a_num
    a_num = ModelType(
        Number,
        required=True,
        metadata=dict(
            description='First input number.'
        )
    )
    
    # * attribute: b_num
    b_num = ModelType(
        Number,
        required=True,
        metadata=dict(
            description='Second input number.'
        )
    )
    
    # * attribute: result
    result = StringType(
        metadata=dict(
            description='Result as a string.'
        )
    )
    ```

- **Functional Artifacts (Methods)**:

  - **Definition**: The static `new()` method (from `ModelObject`) creates validated instances, with optional `validate` and `strict` parameters. Custom methods (e.g., `format` in `Number`, `add` in `Calculation`) encapsulate domain logic.
  - **Purpose**: `new()` enables instantiation (e.g., `ModelObject.new(Number, value="123.45")`), while custom methods handle operations like calculations or formatting.
  - **Example** (from `Calculation` in `app/models/calc.py`):

    ```python
    # * method: add
    def add(self):
        '''
        Adds a_num to b_num.
        '''
        # Add the numbers.
        result = self.a_num.format() + self.b_num.format()
        
        # Set the result.
        self.result = str(result)
    
    # * method: subtract
    def subtract(self):
        '''
        Subtracts b_num from a_num.
        '''
        # Subtract the numbers.
        result = self.a_num.format() - self.b_num.format()
        
        # Set the result.
        self.result = str(result)
    
    # * method: multiply
    def multiply(self):
        '''
        Multiplies a_num by b_num.
        '''
        # Multiply the numbers.
        result = self.a_num.format() * self.b_num.format()
        
        # Set the result.
        self.result = str(result)
    
    # * method: exponentiate
    def exponentiate(self):
        '''
        Raises a_num to the power of b_num.
        '''
        # Exponentiate the numbers.
        result = self.a_num.format() ** self.b_num.format()
        
        # Set the result.
        self.result = str(result)
    ```

## Using Domain Models in Tiferet

The following subsections detail how to define, instantiate, and test models like `Number` and `Calculation` in the `tiferet-calculator-app`.

### Defining Models

- **Where**: Place models in `app/models/` (e.g., `app/models/calc.py`).
- **How**: Inherit from `ValueObject` for value objects (e.g., `Number`) or `Entity` for entities (e.g., `Calculation`). Use Tiferet types (e.g., `StringType`, `ModelType`) with validation rules (e.g., `regex`, `required=True`). Include artifact comments (e.g., `# * attribute: value`) and space attributes with blank lines. Add methods for domain logic (e.g., `Calculation.add`).
- **Example**: The `Number` and `Calculation` models in `app/models/calc.py` (shown above) include artifact comments, spaced attributes, and calculation methods.

### Instantiating Models

- **How**: Use `ModelObject.new(model_type, **kwargs, validate=True, strict=True)` to create instances. Set `validate=False` for trusted configurations to reduce overhead. Import `ModelObject` from `tiferet.models` and application-specific models under a `# ** app` artifact group.
- **Example** (in `app/basic_calc.py`):

  ```python
  # *** imports
  
  # ** infra
  from tiferet.models import ModelObject
  
  # ** app
  from app.models.calc import Number, Calculation
  
  # *** code
  
  # Create Number instances
  number_a = ModelObject.new(Number, value="8.0")
  number_b = ModelObject.new(Number, value="2.0")
  
  # Create Calculation instance
  calc = ModelObject.new(Calculation, a_num=number_a, b_num=number_b)
  
  # Perform addition
  calc.add()
  
  # Print result
  print(f'{calc.a_num.value} + {calc.b_num.value} = {calc.result}')  # Outputs: 8.0 + 2.0 = 10.0
  ```

### Testing Models

- **How**: Test models with `pytest` in `app/models/tests/test_calc.py`, verifying instantiation and methods. Use `pytest` and `tiferet.models` imports, with application-specific models under a `# ** app` artifact group using `from ..calc import *`. Follow the structure of `tiferet/models/tests/test_settings.py` with fixtures and tests.
- **Example** (in `app/models/tests/test_calc.py`):

  ```python
  # *** imports
  
  # ** infra
  import pytest
  from tiferet.models import *
  
  # ** app
  from ..calc import *
  
  # *** fixtures
  
  # ** fixture: test_number
  @pytest.fixture
  def test_number():
      return Number
  
  # ** fixture: test_calculation
  @pytest.fixture
  def test_calculation():
      return Calculation
  
  # *** tests
  
  # ** test: number_valid
  def test_number_valid(test_number):
      num = ModelObject.new(test_number, value="123.45")
      assert num.format() == 123.45
  
  # ** test: calculation_add
  def test_calculation_add(test_calculation):
      calc = ModelObject.new(test_calculation,
          a_num=ModelObject.new(Number, value="5.0"),
          b_num=ModelObject.new(Number, value="3.0")
      )
      calc.add()
      assert calc.result == "8.0"
  ```

## Conclusion

Tiferet’s domain models, exemplified by `Number` (value object) and `Calculation` (entity), embody the framework’s philosophy of beauty in balance. By defining models with clear validation, instantiating them with `ModelObject.new`, and testing them with `pytest`, developers can ensure robust, modular applications like `tiferet-calculator-app`. These models, with their artifact comments and calculation methods, reflect Tiferet’s elegant, configuration-driven design.