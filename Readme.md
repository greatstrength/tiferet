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

```python
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
```

Serialization: The 'to_data' role does not explicitly include 'id', reflecting that components are not identified by a unique ID but by their attributes.

StarshipData
Entities like Starship, which do have identity, require careful handling of their ID:

```python
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
```

Serialization: Here, we've configured 'to_data' to exclude the 'id' when serializing for storage, allowing for scenarios where the ID might be managed differently or not needed in the data storage context.

Usage
From Domain to Data: When you need to persist or serialize your domain objects for storage or transfer, use the from_model method:

```python
starship = Starship.new(name="Enterprise", ...)
starship_data = StarshipData.from_model(starship)
# starship_data can now be serialized to YAML, JSON, or stored in a database
From Data to Domain: To load data back into domain objects for use within your application:
python
# Assuming 'data' is from a YAML file or similar source
starship_data = StarshipData.from_data(**data)
starship = starship_data.map()
# 'starship' is now a domain object ready for use
```

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

```python
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
```

StarshipYamlProxy
A concrete implementation that uses YAML for data storage:

```python
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
```


Why This Matters
Abstraction: Developers can interact with starships without worrying about how they're stored or retrieved, making it easy to switch data storage solutions.
Flexibility: The proxy pattern allows for different implementations (e.g., from YAML to database) without changing the interface or client code.
Simplicity: For demo or development purposes, YAML files offer a straightforward way to manage and share data.

For more advanced usage, including how to configure Tiferet's yaml_client or to implement other data storage solutions like databases, please refer to the advanced documentation sections or the Tiferet wiki.

This documentation snippet introduces developers to the concept of repositories in Tiferet, focusing on YAML as a simple data storage method while hinting at the system's scalability to more complex storage solutions.

-------


You're absolutely right. Let's update the StarshipYamlProxy to include a save method for persisting starship data:

```python
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
```

Usage
Saving a Starship:

```python
repo = StarshipYamlProxy('starships.yml')
new_starship = Starship.new(name="Millennium Falcon", ship_class="Freighter", ...)
repo.save(new_starship)  # This will either update or add the starship to the YAML file
```

Why This Matters
CRUD Operations: Now, developers can perform Create, Read, Update, and Delete operations (though DELETE is not implemented here) on starships through the same repository interface, maintaining consistency in data management.
Persistence: Saving allows for the persistence of changes made to starships, ensuring that the state of your application's data can be preserved between sessions or shared across environments.
Simplicity: By abstracting the save operation, you keep the complexity of dealing with file I/O or database operations away from the core logic, enhancing maintainability.

This addition completes the basic CRUD functionality for the starship example in Tiferet, demonstrating how the framework supports both reading and writing data through a consistent interface.

## Feature Commands

Apps are more than just their shape as defined by Domain Models, but they also contain the necessary interactions between both the required subsystems and the user for the task at hand. Feature commands are a command object that execute such interactions.


Here's a list of feature commands for our Starship application, inspired by the earlier discussions and using the structure you've provided for AddNewFeature and AddFeatureCommand:

```python
# *** imports

# ** app
from ..domain.starship import Starship, StarshipComponent
from ..data.starship import StarshipData, StarshipComponentData
from ..repos.starship import StarshipRepository

class StarshipService(object):
    '''
    The starship service.
    '''

    def __init__(self, starship_repo: StarshipRepository):
        '''
        Initialize the starship service.
        
        :param starship_repo: The starship repository.
        :type starship_repo: StarshipRepository
        '''

        # Set the starship repository.
        self.starship_repo = starship_repo

class CreateStarship(StarshipService):
    '''
    Create a new starship.
    '''

    def execute(self, **kwargs) -> Starship:
        '''
        Execute the command to create a new starship.
        
        :param kwargs: The keyword arguments for starship attributes.
        :type kwargs: dict
        :return: The new starship.
        :rtype: Starship
        '''

        # Create a new starship.
        starship = Starship.new(**kwargs)

        # Assert that the starship does not already exist.
        assert not self.starship_repo.exists(
            starship.id), f'STARSHIP_ALREADY_EXISTS: {starship.id}'

        # Save and return the starship.
        self.starship_repo.save(starship)
        return starship

class AddComponentToStarship(StarshipService):
    '''
    Add a component to a starship.
    '''

    def execute(self, starship_id: str, **kwargs) -> Starship:
        '''
        Execute the command to add a component to a starship.

        :param starship_id: The starship ID.
        :type starship_id: str
        :param kwargs: The keyword arguments for component attributes.
        :type kwargs: dict
        :return: The updated starship.
        :rtype: Starship
        '''

        # Get the starship using the starship ID.
        starship = self.starship_repo.get(starship_id)

        # Assert that the starship was successfully found.
        assert starship is not None, f'STARSHIP_NOT_FOUND: {starship_id}'

        # Create a new component.
        component = StarshipComponent.new(**kwargs)

        # Add the component to the starship.
        starship.add_component(component)

        # Save and return the updated starship.
        self.starship_repo.save(starship)
        return starship

class CalculateStarshipPerformance(StarshipService):
    '''
    Calculate the performance metrics of a starship.
    '''

    def execute(self, starship_id: str) -> dict:
        '''
        Execute the command to calculate starship performance.

        :param starship_id: The starship ID.
        :type starship_id: str
        :return: Performance metrics.
        :rtype: dict
        '''

        # Get the starship using the starship ID.
        starship = self.starship_repo.get(starship_id)

        # Assert that the starship was successfully found.
        assert starship is not None, f'STARSHIP_NOT_FOUND: {starship_id}'

        # Calculate and return performance metrics.
        return starship.calculate_performance()

class SimulateBattle(StarshipService):
    '''
    Simulate a battle between two starships.
    '''

    def execute(self, attacker_id: str, defender_id: str) -> dict:
        '''
        Execute the command to simulate a battle between starships.

        :param attacker_id: The ID of the attacking starship.
        :type attacker_id: str
        :param defender_id: The ID of the defending starship.
        :type defender_id: str
        :return: Battle outcome.
        :rtype: dict
        '''

        # Retrieve both starships.
        attacker = self.starship_repo.get(attacker_id)
        defender = self.starship_repo.get(defender_id)

        # Assert both starships exist.
        assert attacker is not None, f'ATTACKER_NOT_FOUND: {attacker_id}'
        assert defender is not None, f'DEFENDER_NOT_FOUND: {defender_id}'

        # Basic battle simulation logic (this would be more complex in a real scenario)
        attacker_performance = attacker.calculate_performance()
        defender_performance = defender.calculate_performance()

        # Simple battle result based on speed and durability
        if attacker_performance['speed'] > defender_performance['speed']:
            outcome = 'Victory' if attacker_performance['durability'] > defender_performance['durability'] else 'Draw'
        else:
            outcome = 'Defeat' if attacker_performance['durability'] < defender_performance['durability'] else 'Draw'

        return {
            'outcome': outcome,
            'attacker': attacker_id,
            'defender': defender_id
        }

class ListAllStarships(StarshipService):
    '''
    List all starships or filter by class.
    '''

    def execute(self, ship_class: str = None) -> List[Starship]:
        '''
        Execute the command to list all starships.

        :param ship_class: Filter by ship class if provided.
        :type ship_class: str
        :return: List of starships.
        :rtype: List[Starship]
        '''

        # Retrieve all starships, optionally filtered by class.
        return self.starship_repo.list(ship_class)
```

These commands encapsulate various operations on starships, demonstrating how features can be built around domain entities using the repository pattern for data persistence. Each command interacts with the StarshipRepository to perform its task, aligning with Tiferet's philosophy of organizing domain logic through features and commands.


----

## Features

Here's how you might approach documenting the YAML feature configuration for your Tiferet project, particularly focusing on the return_to_data flag:

YAML Feature Configuration in Tiferet
In Tiferet, features are defined using YAML configurations, which provide a clear, external way to describe the flow of operations within your application. Here's how it works with our Starship application:

Structure of Feature Configuration
A feature in YAML typically looks like:

```yaml
features:
  <feature_id>:
    commands:
      - name: <command_name>
        attribute_id: <handler_id>
        params:
          <param_name>: <param_value>
        return_to_data: <true/false>
        data_key: <key_to_store_result>
      - ... # More commands as needed
    name: <Feature Name>
    group_id: <Context Group>
```

Key Elements:
feature_id: A unique identifier for the feature, typically in the format <group_id>.<feature_key>.
commands: A list of FeatureCommands that define the workflow of the feature:
name: A descriptive name for the command, useful for documentation and debugging.
attribute_id: The identifier for the command handler in your code. This is used to dynamically fetch the correct handler at runtime.
params: Parameters needed for the command execution.
return_to_data: 
When true, the result of this command will be stored in the RequestContext data. This is useful for features where subsequent commands need the results from earlier ones. 
When false or omitted, the result is not stored, which is typical for one-off commands or when you want to directly return the result to the caller without further processing in the feature workflow.
data_key: If return_to_data is true, this specifies the key under which the result will be stored in the RequestContext data.
name: Human-readable name of the feature.
group_id: Helps in organizing features by domain or module.


Here's the updated YAML configuration for the Starship application, removing the return_to_data keys for features where they aren't part of a workflow:

Feature Configuration for Starship Application
In Tiferet, features are defined in YAML to describe the behaviors or workflows within your application. Here's how the main features for our Starship application are configured:

YAML Feature Configuration
```yaml
features:
  starship.create:
    commands:
      - name: Create Starship
        attribute_id: create_starship
    name: Create Starship
    group_id: starship

  starship.add_component:
    commands:
      - name: Add Component
        attribute_id: add_component_to_starship
    name: Add Component to Starship
    group_id: starship

  starship.calculate_performance:
    commands:
      - name: Calculate Performance
        attribute_id: calculate_starship_performance
    name: Calculate Starship Performance
    group_id: starship

  starship.battle:
    commands:
      - name: Simulate Battle
        attribute_id: simulate_battle
    name: Starship Battle
    group_id: starship

  starship.list_all:
    commands:
      - name: List All Starships
        attribute_id: list_all_starships
    name: List All Starships
    group_id: starship
```

Explanation:
feature_id: Each feature is uniquely identified by an ID like <group_id>.<feature_key>. The group_id here is starship, indicating the domain context.
commands: Each feature includes one or more commands:
name: Provides a clear description of what the command does.
attribute_id: Points to the specific handler or logic to be executed.
name: Human-readable name for the feature for documentation purposes.
group_id: Organizes features by domain area.

## App Interface

Great to hear it aligns well with your setup! Here's how you might sum it up for your README:

Interface Configuration for Starship Application
Tiferet uses interfaces to define how different parts of your application interact with the user or other systems. For our Starship application, we've set up a simple CLI interface in app/configs/interfaces.yml:

```yaml
interfaces:
  star_cli:
    name: Starship CLI Interface
    data_flag: yaml
```

Explanation:

interface_id: star_cli identifies this interface, used when you run features through app.run().
name: Descriptive name for the interface, helpful for documentation or interface selection.
data_flag: Set to yaml, indicating that data operations will use YAML files for persistence.
Default Contexts: 
App Context: If not specified, it defaults to AppInterfaceContext, which means this CLI interface will use the standard application interface context for managing feature execution.
Error Context: Also not explicitly set here, so it defaults to the ErrorContext provided by Tiferet, ensuring consistent error handling across interfaces.

This setup provides an easy, straightforward way to interact with your Starship application through the command line, with data managed via YAML files and errors handled uniformly.

## Initializer Script


Let's build out some cool ships for a battle scenario. Here's how you might script this using the Tiferet framework with the Starship application we've been discussing:

```python
from tiferet import App
from tiferet.domain.starship import StarshipComponent

# Initialize the Tiferet App
app = App()

# Helper function to create components
def create_component(name, type, power_level):
    return StarshipComponent.new(name=name, type=type, power_level=power_level)

# Create Starships

# Federation Starship: Enterprise
enterprise_data = {
    'name': 'Enterprise',
    'ship_class': 'Explorer'
}
enterprise = app.run('star_cli', feature_id='starship.create', data=enterprise_data)['starship']

# Add components to Enterprise
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=enterprise.id, 
                  component=create_component('Warp Drive', 'Engine', 150)))
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=enterprise.id, 
                  component=create_component('Phaser Banks', 'Weapon', 100)))
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=enterprise.id, 
                  component=create_component('Deflector Shields', 'Shield', 120)))

# Klingon Starship: Bird-of-Prey
bird_of_prey_data = {
    'name': 'Bird-of-Prey',
    'ship_class': 'Fighter'
}
bird_of_prey = app.run('star_cli', feature_id='starship.create', data=bird_of_prey_data)['starship']

# Add components to Bird-of-Prey
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=bird_of_prey.id, 
                  component=create_component('Cloaking Device', 'Stealth', 75)))
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=bird_of_prey.id, 
                  component=create_component('Disruptor Cannons', 'Weapon', 110)))
app.run('star_cli', feature_id='starship.add_component', 
        data=dict(starship_id=bird_of_prey.id, 
                  component=create_component('Regenerative Shields', 'Shield', 90)))

# Starship Battle
battle_result = app.run('star_cli', feature_id='starship.battle', 
                        data=dict(attacker_id=enterprise.id, defender_id=bird_of_prey.id))

# Output the battle result
print("Battle Result:", battle_result)

# List all created starships
all_starships = app.run('star_cli', feature_id='starship.list_all')
print("All Starships:", [ship.name for ship in all_starships])
```

Explanation:
Component Creation: We use a helper function to create StarshipComponent instances with different attributes.
Starship Creation: We create two starships, each with different roles (Explorer for the Federation ship and Fighter for the Klingon ship), showcasing how the starship.create feature is used.
Adding Components: We add specialized components to each ship to reflect their capabilities, using the starship.add_component feature. This shows how the application can be extended to configure ships differently.
Simulating Battle: We then simulate a battle between the two ships, which would use the starship.battle feature to compare their performances based on their components.
Listing Starships: Finally, we list all starships to verify they've been created and added to the system.

This script demonstrates the use of features to manage the lifecycle of starships, from creation to engagement in battle scenarios, all within the context of your Tiferet framework. Remember, the battle logic would be simplified here; in a real application, you might want more complex calculations for battle outcomes.

## Container Attributes


Here's how you might configure the container attributes for your Starship application, focusing on using flags for feature commands and data repositories:

```yaml
attrs: 
  create_starship:
    deps:
      core:
        module_path: app.commands.starship
        class_name: CreateStarship
    type: feature
  
  add_component_to_starship:
    deps:
      core:
        module_path: app.commands.starship
        class_name: AddComponentToStarship
    type: feature
  
  calculate_starship_performance:
    deps:
      core:
        module_path: app.commands.starship
        class_name: CalculateStarshipPerformance
    type: feature
  
  simulate_battle:
    deps:
      core:
        module_path: app.commands.starship
        class_name: SimulateBattle
    type: feature
  
  list_all_starships:
    deps:
      core:
        module_path: app.commands.starship
        class_name: ListAllStarships
    type: feature

  starship_repo:
    deps:
      yaml:
        module_path: app.repos.starship
        class_name: StarshipYamlProxy
        params:
          starship_config_file: 'app/configs/starships.yml'
    type: data

const: 
  env: $env.STARSHIP_ENV  # Example environmental variable for configuration
```

Explanation:
Feature Commands under 'core' Flag: 
All feature-related commands (like create_starship, add_component_to_starship, etc.) are grouped under a core flag. This implies these commands are part of the core functionality of your application and will be used when the 'core' feature flag is active or relevant.
Repository behind 'yaml' Flag: 
The starship_repo is configured with a yaml flag, indicating that this repository uses YAML for data persistence. The StarshipYamlProxy class is specified, along with a parameter pointing to the YAML file where starship data is stored.
Constants:
A simple env constant is included, which could be used to manage different environments or configurations. This is analogous to how you handle environment variables in your auth app.

This structure allows for:
Modular Dependency Management: By tagging dependencies with flags like core or yaml, you can easily switch implementations or configurations based on the context or environment.
Flexibility: If you decide to change how data is stored or how features are implemented, you can update these flags without changing the core code.
Alignment with Tiferet's Philosophy: This setup aligns with the principles of Domain-Driven Design and dependency injection, ensuring that each part of your application can be independently configured and managed.

Remember, this YAML would be part of your app/configs/container.yml file, where these attributes are defined for the ContainerContext to use in setting up injection or dependency resolution at runtime.

---

## Errors


Here's how you might describe error configuration for your README:

Configuring Errors in Tiferet
In Tiferet, errors are configured using YAML to define clear, multilingual error messages. Here's how to set them up for your Starship application:

Error Configuration
Errors are defined in a YAML file, typically named errors.yml:

```yaml
errors: 
  STARSHIP_NOT_FOUND:
    message:
      - lang: en_US
        text: 'The starship with id {} was not found.'
    name: Starship not found
    error_code: 'STARSHIP_NOT_FOUND'
  COMPONENT_IS_REQUIRED:
    message:
      - lang: en_US
        text: 'A required component was not provided.'
    name: Component is required
    error_code: 'COMPONENT_IS_REQUIRED'
  INVALID_SHIP_CLASS:
    message:
      - lang: en_US
        text: 'The ship class {} is not recognized.'
    name: Invalid ship class
    error_code: 'INVALID_SHIP_CLASS'
  BATTLE_DRAW:
    message:
      - lang: en_US
        text: 'The battle between {} and {} resulted in a draw.'
    name: Battle ended in draw
    error_code: 'BATTLE_DRAW'
```

Key Elements:
error_code: A unique string used to identify this error within your application's code.
name: A human-readable explanation of the error, useful for documentation or when logging errors.
message: A list where each entry is:
lang: Specifies the language code for the message.
text: The actual error message, where {} can be placeholders for dynamic content.

Usage:
When you define your application's behavior, you can reference these error codes to return structured error information to clients or log them internally.
This configuration allows for easy updates to error messages or adding new error types without changing the application's code.

For more detailed information on how to create and handle custom errors programmatically, please refer to the Tiferet wiki.



----

## Example calculator app

README for Tiferet Calculator
Introduction
Welcome to the Tiferet Calculator, showcasing how Tiferet can be used for stateless operations with an emphasis on domain-driven design, feature execution, and error management.

Installation
sh
git clone [your-repo-url]
cd tiferet-calculator
pip install -r requirements.txt

Running the App
To run the calculator in CLI:

sh
python main.py

Structure
Domain Models: Define arithmetic operations.
Features: Provide interfaces for calculations.
Feature Commands: Implement calculation logic.
Container Configuration: Manage feature instantiation.
Error Handling: Define and handle errors.

Domain Models
```python
# domain.py
from tiferet import ValueObject, IntegerType, StringType

class Number(ValueObject):
    value = IntegerType(required=True)

class Operation(ValueObject):
    operator = StringType(required=True, choices=['+', '-', '*', '/'])
```

Features and Feature Commands
```yaml
# app/configs/features.yml
features:
  calculator.add:
    commands:
      - name: Add Numbers
        attribute_id: add_numbers
    name: Add Numbers
    group_id: calculator
  calculator.subtract:
    commands:
      - name: Subtract Numbers
        attribute_id: subtract_numbers
    name: Subtract Numbers
    group_id: calculator
  calculator.multiply:
    commands:
      - name: Multiply Numbers
        attribute_id: multiply_numbers
    name: Multiply Numbers
    group_id: calculator
  calculator.divide:
    commands:
      - name: Divide Numbers
        attribute_id: divide_numbers
    name: Divide Numbers
    group_id: calculator
```

Feature Command Implementations
```python
# commands.py
from tiferet import FeatureCommand
from .domain import Number, Operation

class AddNumbers(FeatureCommand):
    def execute(self, num1: Number, num2: Number):
        return Number.new(value=num1.value + num2.value)

class SubtractNumbers(FeatureCommand):
    def execute(self, num1: Number, num2: Number):
        return Number.new(value=num1.value - num2.value)

class MultiplyNumbers(FeatureCommand):
    def execute(self, num1: Number, num2: Number):
        return Number.new(value=num1.value * num2.value)

class DivideNumbers(FeatureCommand):
    def execute(self, num1: Number, num2: Number):
        if num2.value == 0:
            raise ValueError("DIVIDE_BY_ZERO")
        return Number.new(value=num1.value / num2.value)
```

Container Configuration
```yaml
# app/configs/container.yml
attrs:
  add_numbers:
    deps:
      core:
        module_path: app.commands
        class_name: AddNumbers
    type: feature
  subtract_numbers:
    deps:
      core:
        module_path: app.commands
        class_name: SubtractNumbers
    type: feature
  multiply_numbers:
    deps:
      core:
        module_path: app.commands
        class_name: MultiplyNumbers
    type: feature
  divide_numbers:
    deps:
      core:
        module_path: app.commands
        class_name: DivideNumbers
    type: feature
```

Error Configuration
```yaml
# app/configs/errors.yml
errors:
  DIVIDE_BY_ZERO:
    message:
      - lang: en_US
        text: 'Division by zero is not allowed.'
    name: Division by zero
    error_code: 'DIVIDE_BY_ZERO'
```

Main Execution
```python
# main.py
from tiferet import App
from .domain import Number

app = App()

while True:
    operation = input("Enter operation (+, -, *, /) or 'q' to quit: ")
    if operation == 'q':
        break
    
    try:
        num1 = int(input("Enter first number: "))
        num2 = int(input("Enter second number: "))
        
        feature_id = f'calculator.{operation}'
        result = app.run('calc_cli', feature_id=feature_id, data=dict(num1=Number.new(value=num1), num2=Number.new(value=num2)))
        
        if 'error_code' in result:
            print(f"Error: {result['error_code']} - {result['message']}")
        else:
            print(f"Result: {result['value']}")
    except ValueError as e:
        print(f"Error: {str(e)}")
```

Interface Configuration
```yaml
# app/configs/interfaces.yml
interfaces:
  calc_cli:
    name: Calculator CLI Interface
```

Usage
This calculator app demonstrates how Tiferet handles operations and errors:

Add: calculator.add
Subtract: calculator.subtract
Multiply: calculator.multiply
Divide: calculator.divide

The app checks for an error_code in the result, allowing for consistent error handling across features.

Contributing
Expanding this to include more error cases or additional features would further demonstrate Tiferet's robustness in managing both successful operations and error states.

This README now includes error handling, showing how errors are defined, configured, and checked for during application execution. It's a comprehensive view of how Tiferet can manage the lifecycle of operations from start to finish, including error cases.


-----

## In-memory app for Building Ships
I catch your drift perfectly. Let's add an in-memory component management system to our existing Starship application, creating a new interface for it. Here's how we can structure this:

New Feature Configuration for Component Management
First, let's extend the features.yml with new component-related features:

```yaml
# app/configs/features.yml (add these to existing features)
features:
  component.create:
    commands:
      - name: Create Component
        attribute_id: create_component
    name: Create Component
    group_id: component
  component.list:
    commands:
      - name: List Components
        attribute_id: list_components
    name: List Components
    group_id: component
  component.get:
    commands:
      - name: Get Component
        attribute_id: get_component
    name: Get Component
    group_id: component
```

New Feature Command Implementations
Let's create command handlers for these new features:

```python
# commands/component.py
from tiferet import FeatureCommand
from ..domain.starship import StarshipComponent

class CreateComponent(FeatureCommand):
    def execute(self, **kwargs):
        component = StarshipComponent.new(**kwargs)
        # Here, we're just keeping components in memory for simplicity
        if not hasattr(self, 'components'):
            self.components = []
        self.components.append(component)
        return component

class ListComponents(FeatureCommand):
    def execute(self):
        if not hasattr(self, 'components'):
            return []
        return self.components

class GetComponent(FeatureCommand):
    def execute(self, component_id):
        if not hasattr(self, 'components'):
            return None
        # Assuming components have an 'id' attribute for identification
        return next((c for c in self.components if c.id == component_id), None)
```

Update Container Configuration
Add these new commands to the container.yml:

```yaml
# app/configs/container.yml (add these to existing attrs)
attrs:
  create_component:
    deps:
      core:
        module_path: app.commands.component
        class_name: CreateComponent
    type: feature
  list_components:
    deps:
      core:
        module_path: app.commands.component
        class_name: ListComponents
    type: feature
  get_component:
    deps:
      core:
        module_path: app.commands.component
        class_name: GetComponent
    type: feature
```

New Interface Configuration
Add a new interface for component management:

```yaml
# app/configs/interfaces.yml (add this to existing interfaces)
interfaces:
  component_cli:
    name: Component CLI Interface
```

Main Application Script
To use this new interface alongside the existing starship management:

```python
# main.py (assuming this is where you run your app)

from tiferet import App
from app.domain.starship import StarshipComponent

app = App()

def create_component():
    name = input("Enter component name: ")
    type = input("Enter component type: ")
    power_level = int(input("Enter power level: "))
    
    result = app.run('component_cli', feature_id='component.create', data=dict(name=name, type=type, power_level=power_level))
    print(f"Created component: {result.name}")

def list_components():
    components = app.run('component_cli', feature_id='component.list')
    for component in components:
        print(f"Component: {component.name}, Type: {component.type}, Power Level: {component.power_level}")

def get_component():
    component_id = input("Enter component ID to retrieve: ")
    component = app.run('component_cli', feature_id='component.get', data=dict(component_id=component_id))
    if component:
        print(f"Component found: {component.name}, Type: {component.type}, Power Level: {component.power_level}")
    else:
        print("Component not found.")

while True:
    action = input("Choose action (create/list/get/starship/exit): ")
    if action == 'exit':
        break
    elif action == 'create':
        create_component()
    elif action == 'list':
        list_components()
    elif action == 'get':
        get_component()
    elif action == 'starship':
        # Here you would call the existing starship management functions
        print("Starship interface not implemented in this example.")
    else:
        print("Invalid action.")
```

Concept Explanation
Same App, Different Interfaces: By adding a component_cli interface, you're expanding the application's capabilities without altering its core structure. Each interface can manage its own context group (component for components, starship for starships), allowing for modular expansion of the app's functionality.
In-Memory Management: For simplicity, we've managed components in memory, but this could easily be adapted to use a more permanent storage solution if needed.
Integration: The main script now serves both starship and component functionalities, demonstrating how different interfaces can coexist and share the same application context.

This setup illustrates how Tiferet can be used to build applications with multiple, distinct functionalities under a unified framework, promoting modularity and reuse.

---

## New Documentation Idea


That's an excellent plan for structuring your Tiferet applications. Here’s how we might outline this approach:

Shipbuilder App - In-Memory
Purpose: A lightweight, in-memory application for creating and managing starships with components.

Domain Models:
Starship: An entity with attributes like name, class, speed, durability, and a list of components.
StarshipComponent: A value object representing different parts of a starship (engines, weapons, etc.).

Features:
component.create - Create a new component.
component.list - List all components in memory.
starship.create - Create a new starship with components.
starship.add_component - Add a component to an existing starship.

Commands:
CreateComponent: Adds a new component to an in-memory list.
ListComponents: Lists all components currently in memory.
CreateStarship: Creates a starship instance with given attributes and components.
AddComponentToStarship: Adds a component to a starship.

Interfaces:
builder_cli: Command-line interface for building starships.

Space Battle App - With Persistence
Purpose: An application for simulating battles between starships, with data persistence for battle results and ship configurations.

Domain Models:
Battle: An entity to store battle information, including participants (ships) and outcome.
Starship and StarshipComponent: Reuse or extend from Shipbuilder, ensuring they can be serialized for persistence.

Data Models:
BattleData: To persist battle outcomes, including references to starships or their IDs.
StarshipData: For persisting ship configurations before battles.

Features:
battle.simulate - Simulate a battle between two starships.
battle.list - List previous battles or battle summaries.
battle.get - Retrieve details of a specific battle.

Commands:
SimulateBattle: Takes two starships, simulates a battle, and persists the result.
ListBattles: Retrieves and lists battle data from storage.
GetBattle: Fetches a specific battle by ID or other criteria.

Repositories:
BattleRepository: To save, list, and retrieve battle data.

Interfaces:
battle_cli: Command-line interface for managing and simulating battles.

Implementation Strategy:
Shipbuilder:
Use in-memory lists or similar structures for components and starships. No need for persistence here.
CLI for user interaction to create and manage starships.
Space Battle App:
Implement Battle as an entity with methods to encapsulate battle logic.
Use YAML or another simple format for data persistence, focusing on BattleData and possibly StarshipData.
CLI for running simulations, viewing battle history, or getting details of past battles.

Integration:
Data Transfer: When moving from Shipbuilder to Space Battle App, you could serialize the Starship (and its components) into a format (like JSON) that the Battle App can then deserialize into its domain models or data models for persistence.
Shared Domain Models: Ensure that Starship and StarshipComponent are defined in a way that can be shared or extended between apps for consistency.

This dual-app approach provides a clear separation of concerns while showcasing different aspects of Tiferet's capabilities — from in-memory manipulation to data persistence, all within a cohesive domain-driven framework. It also offers a practical example of how applications can interact, with one preparing data for another to consume and process.


----

## Updated Starship Code

Thank you for the clarification and the updated FeatureContext code. Here's how the Shipbuilder app would look with these adjustments:

Domain Models
```python
# app/domain/starship.py
from tiferet import Entity, ValueObject, StringType, FloatType, IntegerType, ListType, ModelType

class StarshipComponent(ValueObject):
    name = StringType(required=True, metadata=dict(description='Component name.'))
    type = StringType(required=True, metadata=dict(description='Component type.'))
    power_level = IntegerType(required=True, metadata=dict(description='Component power level.'))

    @staticmethod
    def new(**kwargs):
        return super().new(StarshipComponent, **kwargs)

class Starship(Entity):
    id = StringType(required=True, metadata=dict(description='Unique identifier for the starship.'))
    name = StringType(required=True, metadata=dict(description='Starship name.'))
    ship_class = StringType(required=True, metadata=dict(description='Starship class.'))
    components = ListType(ModelType(StarshipComponent), default=[], metadata=dict(description='Components of the starship.'))
    
    @staticmethod
    def new(**kwargs):
        return super().new(Starship, **kwargs)
```

Feature Configuration
```yaml
# app/configs/features.yml
features:
  starship.start_building:
    commands:
      - name: Start Building Starship
        attribute_id: start_building_starship
        return_to_data: true
        data_key: starship_id
        save_to_cache: true
    name: Start Building Starship
    group_id: starship
  starship.add_component:
    commands:
      - name: Add Component
        attribute_id: add_component
        return_to_data: false
        save_to_cache: true
        data_key: starship_id
    name: Add Component to Starship
    group_id: starship
  starship.remove_component:
    commands:
      - name: Remove Component
        attribute_id: remove_component
        return_to_data: false
        save_to_cache: true
        data_key: starship_id
    name: Remove Component from Starship
    group_id: starship
  starship.finalize:
    commands:
      - name: Finalize Starship
        attribute_id: finalize_starship
    name: Finalize Starship
    group_id: starship
```

Commands
```python
# app/commands/starship.py
from tiferet import FeatureCommand
from ..domain.starship import Starship, StarshipComponent
import uuid

class StartBuildingStarship(FeatureCommand):
    def execute(self, **kwargs):
        starship = Starship.new(id=str(uuid.uuid4()), **kwargs)
        return starship.id

class AddComponent(FeatureCommand):
    def execute(self, starship_id: str, component: dict, cache: dict = {}, **kwargs):
        if starship_id not in cache:
            raise ValueError("Starship not in cache")
        starship = cache[starship_id]
        component_obj = StarshipComponent.new(**component)
        starship.components.append(component_obj)
        cache[starship_id] = starship
        return starship_id

class RemoveComponent(FeatureCommand):
    def execute(self, starship_id: str, component_type: str, cache: dict = {}, **kwargs):
        if starship_id not in cache:
            raise ValueError("Starship not in cache")
        starship = cache[starship_id]
        starship.components = [c for c in starship.components if c.type != component_type]
        cache[starship_id] = starship
        return starship_id

class FinalizeStarship(FeatureCommand):
    def execute(self, starship_id: str, cache: dict = {}, **kwargs):
        if starship_id not in cache:
            raise ValueError("Starship not in cache")
        starship = cache.pop(starship_id)  # Remove from cache after finalization
        return starship.to_primitive()
```

Main Execution (CLI)
```python
# main.py
from tiferet import App

app = App()

def build_starship():
    name = input("Enter starship name: ")
    ship_class = input("Enter starship class: ")
    starship_id = app.run('builder_cli', feature_id='starship.start_building', data=dict(name=name, ship_class=ship_class))['starship_id']

    while True:
        action = input("Add component (add), Remove component (remove), or Finalize (finalize)? ")
        if action == 'add':
            component = {
                'name': input("Component name: "),
                'type': input("Component type: "),
                'power_level': int(input("Component power level: "))
            }
            app.run('builder_cli', feature_id='starship.add_component', data=dict(starship_id=starship_id, component=component))
        elif action == 'remove':
            component_type = input("Enter component type to remove: ")
            app.run('builder_cli', feature_id='starship.remove_component', data=dict(starship_id=starship_id, component_type=component_type))
        elif action == 'finalize':
            starship = app.run('builder_cli', feature_id='starship.finalize', data=dict(starship_id=starship_id))
            return starship
        else:
            print("Invalid action")

while True:
    action = input("Build a new starship? (yes/no): ")
    if action.lower() == 'yes':
        starship = build_starship()
        print(f"Starship built: {starship}")
    elif action.lower() == 'no':
        break
    else:
        print("Invalid input")
```

Notes:
App as Builder: The application itself acts as the builder by managing the lifecycle of the starship through features and commands, with the cache serving as an in-memory state for the building process.
Starship Entity: The Starship entity now includes an id for caching purposes, and the actual building happens through modifications in the cache.
Cache Management: Commands interact with the cache directly. The FinalizeStarship command removes the starship from the cache to invalidate it after construction is complete.
Error Handling: Basic error checks for cache existence are included, but for a production application, you'd want more robust error handling and perhaps cache management strategies (like cache expiration).

---

## Ship Builder Feature Command Code and Feature Config

```python
# app/commands/starship.py
from tiferet import FeatureCommand
from ..domain.starship import Starship, StarshipComponent
import uuid

class StartBuildingStarship(FeatureCommand):
    def execute(self, cache_context: CacheContext, **kwargs):
        starship = Starship.new(id=str(uuid.uuid4()), **kwargs)
        cache_context.set('current_starship', starship)

class AddComponent(FeatureCommand):
    def execute(self, component: dict, cache_context: CacheContext, **kwargs):
        starship = cache_context.get('current_starship')
        if not starship:
            raise ValueError("Starship not in cache")
        component_obj = StarshipComponent.new(**component)
        starship.components.append(component_obj)
        cache_context.set('current_starship', starship)

class RemoveComponent(FeatureCommand):
    def execute(self, component_type: str, cache_context: CacheContext, **kwargs):
        starship = cache_context.get('current_starship')
        if not starship:
            raise ValueError("Starship not in cache")
        starship.components = [c for c in starship.components if c.type != component_type]
        cache_context.set('current_starship', starship)

class FinalizeStarship(FeatureCommand):
    def execute(self, cache_context: CacheContext, **kwargs):
        starship = cache_context.get('current_starship')
        if not starship:
            raise ValueError("Starship not in cache")
        cache_context.delete('current_starship')  # Remove from cache after finalization
        return starship.to_primitive()  # Only this command returns something as it finalizes the starship
```

```yaml
# app/configs/features.yml
features:
  starship.start_building:
    commands:
      - name: Start Building Starship
        attribute_id: start_building_starship
    name: Start Building Starship
    group_id: starship
  starship.add_component:
    commands:
      - name: Add Component
        attribute_id: add_component
    name: Add Component to Starship
    group_id: starship
  starship.remove_component:
    commands:
      - name: Remove Component
        attribute_id: remove_component
    name: Remove Component from Starship
    group_id: starship
  starship.finalize:
    commands:
      - name: Finalize Starship
        attribute_id: finalize_starship
    name: Finalize Starship
    group_id: starship
  starship.clear:
    commands:
      - name: Clear Ship from Builder
        attribute_id: clear_ship_from_builder
    name: Clear Ship from Builder
    group_id: starship
```

## Container Attribute Configurations
```yaml
# app/configs/container.yml
attrs: 
  start_building_starship:
    deps:
      core:
        module_path: app.commands.starship
        class_name: StartBuildingStarship
    type: feature
  add_component:
    deps:
      core:
        module_path: app.commands.starship
        class_name: AddComponent
    type: feature
  remove_component:
    deps:
      core:
        module_path: app.commands.starship
        class_name: RemoveComponent
    type: feature
  finalize_starship:
    deps:
      core:
        module_path: app.commands.starship
        class_name: FinalizeStarship
    type: feature
  clear_ship_from_builder:
    deps:
      core:
        module_path: app.commands.starship
        class_name: ClearShipFromBuilder
    type: feature
```