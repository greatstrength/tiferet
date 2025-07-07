# Tiferet Models Documentation

This document serves as an educational guide for human and AI developers to understand, define, and use domain models in the Tiferet framework, a modular, configuration-driven platform inspired by Domain-Driven Design (DDD) and the Kabbalistic principle of beauty in balance. Using the `tiferet-calculator-app`, it explains domain models, their static and functional artifacts, the distinction between entities and value objects, and how to define, instantiate, and test models, with practical code examples and formatting.
## What Are Domain Models?

In Domain-Driven Design (DDD), domain models are the conceptual heart of an application, encapsulating the core data, behavior, and rules of the problem domain to create a shared, structured representation that aligns technical implementation with business needs. They enable developers and stakeholders to collaborate effectively by modeling real-world concepts—such as calculations or numeric inputs in the `tiferet-calculator-app`—in a way that is both precise and expressive, driving the application’s logic and ensuring consistency. In Tiferet, domain models are immutable objects built on `ValueObject` or `Entity` base classes, leveraging types like `StringType` and `ModelType` to enforce immutability, type safety, and robust validation. These models form the foundation of Tiferet’s DDD approach, balancing simplicity and rigor to represent domain concepts like calculator inputs or results, seamlessly integrating with configurations, commands, and contexts to create elegant, modular applications.

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
        def set_result(self, result: str = None):
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
    ```

## Static and Functional Artifacts

Domain models consist of static attributes and functional methods, leveraging Tiferet types:

- **Static Artifacts (Attributes)**:

  - **Definition**: Attributes represent the model’s state, capturing the current values of its properties, which may change based on the situation (e.g., `result` in `Calculation` updated after an operation). They use Tiferet types (e.g., `StringType`, `ModelType`) with validation rules (e.g., `required=True`, `regex`, `default=''`) to define the ideal or “model” state, embodying “what is good” or expected behavior for the domain.

  - **Purpose**: Attributes like `value` in `Number` or `a_num` and `result` in `Calculation` store and validate domain data, ensuring consistency and correctness. For example, `result: StringType(default='')` ensures an empty string as the initial state, updated only through valid operations.

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
        default='',
        metadata=dict(
            description='Result as a string.'
        )
    )
    ```

- **Functional Artifacts (Methods)**:

  - **Definition**: Methods manage and adjust the model’s state according to domain-specific intentions, either by modifying internal state (e.g., updating `result` via `set_result`) or incorporating external data (e.g., from command inputs).

  - **Purpose**: Methods like `add` or `set_result` in `Calculation` perform operations (e.g., addition) and update attributes (e.g., `result`) to reflect the domain’s intent, ensuring controlled state changes within the model’s immutable framework.

  - **Example** (from `Calculation` in `app/models/calc.py`):

    ```python
    # * method: set_result
    def set_result(self, result: str = None):
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

## Using Domain Models in Tiferet

The following subsections detail how to define, instantiate, and test models like `Number` and `Calculation` in the `tiferet-calculator-app`.

### Defining Models

- **How**: Inherit from `ValueObject` for value objects (e.g., `Number`) or `Entity` for entities (e.g., `Calculation`). Use Tiferet types (e.g., `StringType`, `ModelType`) with validation rules (e.g., `regex`, `required=True`, `default=''`). Add methods for domain logic (e.g., `Calculation.add`).
- **Example**: The `Number` and `Calculation` models in `app/models/calc.py` (shown above) include spaced attributes and calculation methods.

### Instantiating Models

- **How**: Use `ModelObject.new(model_type, **kwargs, validate=True, strict=True)` to create instances. Set `validate=False` for trusted configurations to reduce overhead. Import `ModelObject` from `tiferet.models`.

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

- **How**: Test models with `pytest` in `app/models/tests/test_calc.py`, verifying instantiation and methods. Use `pytest` and `tiferet.models` imports along with application-specific models using `from ..calc import *`. Follow a structured approach with fixtures and tests.

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

Tiferet’s domain models, exemplified by `Number` (value object) and `Calculation` (entity), embody the framework’s philosophy of beauty in balance. By defining models with clear validation and state management, instantiating them with `ModelObject.new`, and testing them with `pytest`, developers can ensure robust, modular applications like `tiferet-calculator-app`. These models, with their state-managing methods, reflect Tiferet’s elegant, configuration-driven design.