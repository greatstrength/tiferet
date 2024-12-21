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


## Repositories and Proxies


Here's how you might document this repository approach for your README, keeping the explanation simple and focused on the basics:

Using Repositories for Data Management in Tiferet
Tiferet leverages repositories and their proxies to manage data, providing a layer of abstraction between your domain logic and data persistence. Here's an example with our starship application using a YAML file for data storage:

StarshipRepository Interface
An interface defines the contract for all starship repositories:

python
from typing import List
from ..domain.starship import Starship

class StarshipRepository:
    '''
    Starship repository interface.
    '''

    def exists(self, id: str) -> bool:
        '''
        Check if a starship with the given id exists.
        '''
        raise NotImplementedError()

    def get(self, id: str) -> Starship:
        '''
        Retrieve a starship by its id.
        '''
        raise NotImplementedError()

    def list(self, ship_class: str = None) -> List[Starship]:
        '''
        List all starships, optionally filtered by class.
        '''
        raise NotImplementedError()

StarshipYamlProxy
A concrete implementation that uses YAML for data storage:

python
from ..data.starship import StarshipData
from ..clients import yaml_client

class StarshipYamlProxy(StarshipRepository):
    '''
    YAML repository for starships.
    '''

    def __init__(self, starship_config_file: str):
        '''
        Initialize with the path to the YAML config file.
        '''
        self.config_file = starship_config_file

    def exists(self, id: str) -> bool:
        return self.get(id) is not None

    def get(self, id: str) -> Starship:
        '''
        Load a starship from YAML.
        '''
        starship_data = yaml_client.load(
            self.config_file,
            create_data=lambda data: StarshipData.from_data(id=id, **data),
            start_node=lambda data: data.get('starships', {}).get(id)
        )
        return starship_data.map() if starship_data else None

    def list(self, ship_class: str = None) -> List[Starship]:
        '''
        Load all starships from YAML, optionally filter by class.
        '''
        starships = yaml_client.load(
            self.config_file,
            create_data=lambda data: [StarshipData.from_data(id=id, **starship_data) for id, starship_data in data.get('starships', {}).items()],
            start_node=lambda data: data
        )
        if ship_class:
            starships = [s for s in starships if s.ship_class == ship_class]
        return [s.map() for s in starships]

Usage
Checking if a Starship Exists:

python
repo = StarshipYamlProxy('starships.yml')
exists = repo.exists('enterprise')
print(f"Enterprise exists: {exists}")

Retrieving a Starship:

python
enterprise = repo.get('enterprise')
if enterprise:
    print(f"Retrieved: {enterprise.name}, Class: {enterprise.ship_class}")

Listing Starships:

python
all_fighters = repo.list(ship_class='Fighter')
for ship in all_fighters:
    print(f"Ship: {ship.name}, Class: {ship.ship_class}")

Why This Matters
Abstraction: Developers can interact with starships without worrying about how they're stored or retrieved, making it easy to switch data storage solutions.
Flexibility: The proxy pattern allows for different implementations (e.g., from YAML to database) without changing the interface or client code.
Simplicity: For demo or development purposes, YAML files offer a straightforward way to manage and share data.

For more advanced usage, including how to configure Tiferet's yaml_client or to implement other data storage solutions like databases, please refer to the advanced documentation sections or the Tiferet wiki.

This documentation snippet introduces developers to the concept of repositories in Tiferet, focusing on YAML as a simple data storage method while hinting at the system's scalability to more complex storage solutions.

-------


You're absolutely right. Let's update the StarshipYamlProxy to include a save method for persisting starship data:

python
from typing import List
from ..domain.starship import Starship
from ..data.starship import StarshipData
from ..clients import yaml_client

class StarshipRepository:
    '''
    Starship repository interface.
    '''

    def exists(self, id: str) -> bool:
        '''
        Check if a starship with the given id exists.
        '''
        raise NotImplementedError()

    def get(self, id: str) -> Starship:
        '''
        Retrieve a starship by its id.
        '''
        raise NotImplementedError()

    def list(self, ship_class: str = None) -> List[Starship]:
        '''
        List all starships, optionally filtered by class.
        '''
        raise NotImplementedError()

    def save(self, starship: Starship):
        '''
        Save or update a starship.
        '''
        raise NotImplementedError()

class StarshipYamlProxy(StarshipRepository):
    '''
    YAML repository for starships.
    '''

    def __init__(self, starship_config_file: str):
        '''
        Initialize with the path to the YAML config file.
        '''
        self.config_file = starship_config_file

    def exists(self, id: str) -> bool:
        return self.get(id) is not None

    def get(self, id: str) -> Starship:
        '''
        Load a starship from YAML.
        '''
        starship_data = yaml_client.load(
            self.config_file,
            create_data=lambda data: StarshipData.from_data(id=id, **data),
            start_node=lambda data: data.get('starships', {}).get(id)
        )
        return starship_data.map() if starship_data else None

    def list(self, ship_class: str = None) -> List[Starship]:
        '''
        Load all starships from YAML, optionally filter by class.
        '''
        starships = yaml_client.load(
            self.config_file,
            create_data=lambda data: [StarshipData.from_data(id=id, **starship_data) for id, starship_data in data.get('starships', {}).items()],
            start_node=lambda data: data
        )
        if ship_class:
            starships = [s for s in starships if s.ship_class == ship_class]
        return [s.map() for s in starships]

    def save(self, starship: Starship):
        '''
        Save or update a starship in YAML.
        '''
        # Convert Starship to StarshipData for serialization
        starship_data = StarshipData.from_model(starship)
        
        # Load the current state of starships
        all_starships = yaml_client.load(
            self.config_file,
            create_data=lambda data: data.get('starships', {}),
            start_node=lambda data: data
        )

        # Update or add the starship in the dictionary
        all_starships[starship.id] = starship_data.to_primitive(role='to_data')
        
        # Write the updated dictionary back to YAML
        yaml_client.write(
            self.config_file,
            data={'starships': all_starships}
        )

Usage
Saving a Starship:

python
repo = StarshipYamlProxy('starships.yml')
new_starship = Starship.new(name="Millennium Falcon", ship_class="Freighter", ...)
repo.save(new_starship)  # This will either update or add the starship to the YAML file

Why This Matters
CRUD Operations: Now, developers can perform Create, Read, Update, and Delete operations (though DELETE is not implemented here) on starships through the same repository interface, maintaining consistency in data management.
Persistence: Saving allows for the persistence of changes made to starships, ensuring that the state of your application's data can be preserved between sessions or shared across environments.
Simplicity: By abstracting the save operation, you keep the complexity of dealing with file I/O or database operations away from the core logic, enhancing maintainability.

This addition completes the basic CRUD functionality for the starship example in Tiferet, demonstrating how the framework supports both reading and writing data through a consistent interface.

## Feature Commands

Apps are more than just their shape as defined by Domain Models, but they also contain the necessary interactions between both the required subsystems and the user for the task at hand. Feature commands are a command object that execute such interactions.

#### Example

Here is a list of feature commands for our Spaceship app:
