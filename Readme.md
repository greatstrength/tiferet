
Domain Models
General Intro:

Domain models are crucial in software architecture, particularly within the context of Domain-Driven Design (DDD). They translate business concepts and rules into concrete data structures, providing a structured representation of the domain's knowledge. Domain models help in understanding, discussing, and refining the domain language and logic, ensuring that the software reflects the real-world processes or entities it aims to represent. They include various elements like entities, value objects, services, and repositories, each serving a specific purpose in capturing the business domain's complexity.

Entities
General Intro:

Entities are a core concept in domain modeling, representing objects that have an identity within the system. Unlike other data structures where equality might be based on attribute values, entities are primarily defined by their unique identifiers. This means that even if two entities have the same attribute values, they are considered different if their identities differ. Entities can change over time, maintaining their identity while their state might evolve. They encapsulate business logic related to their identity and state changes, making them central to business processes and workflows.

Starship Example:

Here's a simplified version of the Starship entity without components:

python
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

In this example, Starship is defined as an Entity with attributes like name, ship_class, speed, and durability. Each starship instance would have a unique id (implied by inheriting from Entity), which distinguishes it from others even if all other attributes are identical. This model captures the essence of a starship in a domain where identity is key, allowing for operations like tracking, updating, or interacting with individual starships over time.


Value Objects
General Intro:

Value Objects are another fundamental element in domain modeling, contrasting with entities by not having an inherent identity. Instead, value objects are defined by their attributes, meaning two value objects with identical attribute values are considered the same. They are immutable, ensuring that once created, their state does not change; if modification is needed, a new instance is created. Value objects are used to model concepts where the value of the object's data is more important than its identity, which is ideal for representing parts, measurements, or any concept where equality is based on value rather than reference.

Starship Components as Value Objects:

Here's how StarshipComponent can be introduced as a value object:

python
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
        metadata=dict(description='Component name.')
    )

    # * attribute: type
    type = StringType(
        required=True,
        metadata=dict(description='Component type (e.g., Engine, Shield, Weapon).')
    )

    # * attribute: power_level
    power_level = IntegerType(
        required=True,
        metadata=dict(description='Component power or efficiency level.')
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'StarshipComponent':
        '''Initialize a new component.'''
        return super().new(StarshipComponent, **kwargs)

Behaviors with Entities
Introducing Behaviors:

Entities not only carry data but also behavior. This behavior often involves operations that can change the state of the entity or compute results based on its state. 

Performance Calculation Method:

For our Starship entity, let's add a method to calculate performance, which leverages the components (value objects):

python
# ** model: starship
class Starship(Entity):
    # ... (previous attributes)

    # * attribute: components
    components = ListType(
        ModelType(StarshipComponent),
        default=[],
        metadata=dict(description='Ship components.')
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'Starship':
        '''Initialize a new starship.'''
        return super().new(Starship, **kwargs)

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

Explanation of Behaviors:

add_component: This method allows modifying the Starship entity by adding a StarshipComponent (value object). It's an example of behavior where the entity's state changes.
calculate_performance: Here, we use the components to compute performance metrics. Since components are value objects, their values (like power_level) directly influence the starship's attributes (speed and durability). This method showcases how entities can use value objects to derive or compute aspects of their behavior without altering the components themselves, maintaining the immutability principle of value objects.

This interaction between entities and value objects illustrates how domain models can encapsulate complex domain logic, providing a structured way to manage both data and behavior within the context of your application's domain.