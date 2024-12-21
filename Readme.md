
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