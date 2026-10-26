__version__ = "1.0.0"

from .base import Entity, MobileEntity
from .herbivore import Herbivore
from .omnivore import Omnivore
from .plant import Plant
from .predator import Predator
from .static_entity import StaticEntity

__all__ = [
    "Entity",
    "MobileEntity",
    "Herbivore",
    "Omnivore",
    "Plant",
    "Predator",
    "StaticEntity",
]