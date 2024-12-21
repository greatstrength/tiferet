# Building an App
## Domain Models

When building an app to effectively capture real-world processes in software, Domain models are crucial for translating business concepts and rules into concrete data structures, providing a structured representation of the domain's knowledge. Domain models help in understanding, discussing, and refining the domain language and logic, ensuring that the software reflects the real-world processes or entities it aims to represent.

### Entities

Entities are a core concept in domain modeling, representing objects that have an identity within the system. Unlike other data structures where equality might be based on attribute values, entities are primarily defined by their unique identifiers. This means that even if two entities have the same attribute values, they are considered different if their identities differ. Entities can change over time, maintaining their identity while their state might evolve. They encapsulate business logic related to their identity and state changes, making them central to business processes and workflows.

#### Example:

Here we have a simple example of our starship as defined by a domain model:

```python
# *** imports

# ** infra
from tiferet import Entity, StringType, FloatType, IntegerType

# *** constants

# */ list[str]
STARSHIP_CLASS_CHOICES = [
    'Explorer',
    'Fighter',
    'Freighter',
    'Battleship'
]

# *** models

# ** model: starship
class Starship(Entity):
    '''
    Represents a starship with basic attributes.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the starship.'
        )
    )

    # * attribute: ship_class
    ship_class = StringType(
        required=True,
        choices=STARSHIP_CLASS_CHOICES,
        metadata=dict(
            description='The class of the starship which dictates its primary role.'
        )
    )

    # * attribute: speed
    speed = FloatType(
        default=0.0,
        metadata=dict(
            description='The speed of the starship in some arbitrary units.'
        )
    )

    # * attribute: durability
    durability = IntegerType(
        default=100,
        metadata=dict(
            description='The durability or health of the starship.'
        )
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'Starship':
        '''
        Initializes a new Starship object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Starship object.
        :rtype: Starship
        '''

        # Create and return a new Starship object.
        return super(Starship, Starship).new(
            Starship,
            **kwargs
        )
```

In this example, Starship is defined as an Entity with attributes like name, ship_class, speed, and durability. Each starship instance would have a unique id (implied by inheriting from Entity), which distinguishes it from others even if all other attributes are identical. This model captures the essence of a starship in a domain where identity is key, allowing for operations like tracking, updating, or interacting with individual starships over time.


### Value Objects

Value Objects, unlike entities that rely upon their intrinsic identity. Instead, value objects are defined by their attributes, meaning two value objects with identical attribute values are considered the same. Value objects are used to model concepts where the value of the object's data is more important than its identity, which is ideal for representing parts, measurements, or any concept where equality is based on value rather than reference.

#### Example:

Here's how we can incorporate a Value Object as a Starship Component. This component serves as the principle means of starship operation:

```python
# ** infra
from tiferet import ValueObject, StringType, IntegerType

# ** model: starship_component
class StarshipComponent(ValueObject):
    '''
    Represents a component of a starship like engines, shields, or weapons.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='Component name.'
        ),
    )

    # * attribute: type
    type = StringType(
        required=True,
        metadata=dict(
            description='Component type (e.g., Engine, Shield, Weapon).'
        ),
    )

    # * attribute: power_level
    power_level = IntegerType(
        required=True,
        metadata=dict(
            description='Component power or efficiency level.'
        ),
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'StarshipComponent':
        '''Initialize a new component.'''

        # Return a new component.
        return super(StarshipComponent, StarshipComponent).new(StarshipComponent, **kwargs)
```

### Model Behaviors with Entities

Entities not only carry data but also behavior. This behavior often involves operations that can change the state of the entity or compute results based on its state. 

#### Example

For our Starship entity, let's add both a method to add a new component calculate performance, which leverages the components (value objects):

```python
# ** model: starship
class Starship(Entity):
    # ... (previous attributes)

    # * attribute: components
    components = ListType(
        ModelType(StarshipComponent),
        default=[],
        metadata=dict(
            description='Ship components.'
        ),
    )

    # ... (previous methods)

    # * method: add_component
    def add_component(self, component: StarshipComponent):
        '''Add a component to the starship.'''
        self.components.append(component)

    # * method: calculate_performance
    def calculate_performance(self) -> dict:
        '''
        Calculate performance metrics based on components.
        '''
        total_power = sum(comp.power_level for comp in self.components)
        return {
            'speed': self.speed + (total_power * 0.1),  # Speed boost based on power
            'durability': self.durability + (total_power // 5)  # Durability increase
        }

```

The add_component method allows modifying the Starship entity by adding a StarshipComponent (value object). It's an example of behavior where the entity's state changes.
The calculate_performance uses the components to compute performance metrics. Since components are value objects, their values (like power_level) directly influence the starship's attributes (speed and durability). This method showcases how entities can use value objects to derive or compute aspects of their behavior without altering the components themselves, maintaining the immutability principle of value objects.

## Data Models

Data Persistence in Tiferet for Starships
To demonstrate how Tiferet handles data persistence, we've created data models for our starship application. These models allow for seamless transitions between domain logic and data storage, ensuring both flexibility and integrity.

StarshipComponentData
Value objects like StarshipComponent don't have an inherent identity, so when we model them for data persistence, we focus on their attributes:

python
from tiferet import DataObject
from ..domain.starship import StarshipComponent

class StarshipComponentData(StarshipComponent, DataObject):
    '''
    A data representation of a starship component for storage.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.allow()
        }

    def map(self, role: str = 'to_model', **kwargs):
        '''
        Maps the component data to a StarshipComponent domain object.
        '''
        return super().map(StarshipComponent, role, **kwargs)

    @staticmethod
    def from_data(**kwargs):
        '''
        Initializes a new StarshipComponentData object from raw data.
        '''
        return super(StarshipComponentData, StarshipComponentData).from_data(
            StarshipComponentData, 
            **kwargs
        )

    @staticmethod
    def from_model(model: StarshipComponent, **kwargs):
        '''
        Initializes a new StarshipComponentData object from a StarshipComponent domain object.
        '''
        return DataObject.from_model(
            StarshipComponentData, 
            model, 
            **kwargs
        )

Serialization: The 'to_data' role does not explicitly include 'id', reflecting that components are not identified by a unique ID but by their attributes.

StarshipData
Entities like Starship, which do have identity, require careful handling of their ID:

python
from tiferet import DataObject
from ..domain.starship import Starship
from .starship_component_data import StarshipComponentData

class StarshipData(Starship, DataObject):
    '''
    A data representation of a starship for storage.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    components = ListType(ModelType(StarshipComponentData), default=[], metadata=dict(description='List of components.'))

    # Methods for mapping and data creation are similar to StarshipComponentData but tailored for Starship

Serialization: Here, we've configured 'to_data' to exclude the 'id' when serializing for storage, allowing for scenarios where the ID might be managed differently or not needed in the data storage context.

Usage
From Domain to Data: When you need to persist or serialize your domain objects for storage or transfer, use the from_model method:
python
starship = Starship.new(name="Enterprise", ...)
starship_data = StarshipData.from_model(starship)
# starship_data can now be serialized to YAML, JSON, or stored in a database
From Data to Domain: To load data back into domain objects for use within your application:
python
# Assuming 'data' is from a YAML file or similar source
starship_data = StarshipData.from_data(**data)
starship = starship_data.map()
# 'starship' is now a domain object ready for use

Why This Matters
Flexibility: This dual-model approach allows for different representations of data based on context (domain logic vs. storage), providing control over what is persisted or transferred.
Domain-Driven Design: It supports the principles of DDD by clearly delineating between domain objects and their data representations, ensuring domain logic remains pure while data is managed effectively.
Scalability: By designing data models this way, your application can scale from simple YAML configurations to complex database schemas without altering domain logic.

Remember, these data models are part of a larger ecosystem where features, commands, and contexts work together to create a fully functional application with Tiferet.

This snippet gives a more complete picture of how one data model (StarshipComponentData) works, including its methods for data transformation, which should help developers grasp the full functionality of your data persistence layer.


## Feature Commands

Apps are more than just their shape as defined by Domain Models, but they also contain the necessary interactions between both the required subsystems and the user for the task at hand. Feature commands are a command object that execute such interactions.

#### Example

Here is a list of feature commands for our Spaceship app:


