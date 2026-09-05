"""
Feast Entity Definitions for Myntra Sense Feature Store.
Defines User, Product, and User-Product Interaction entities.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Entity:
    name: str
    value_type: str
    description: str
    join_key: str


# Core Entities
user_entity = Entity(
    name="user_id",
    value_type="STRING",
    description="Unique identifier for Myntra registered user",
    join_key="user_id"
)

product_entity = Entity(
    name="product_id",
    value_type="STRING",
    description="Catalog SKU identifier for fashion product",
    join_key="product_id"
)

user_session_entity = Entity(
    name="session_id",
    value_type="STRING",
    description="Unique active session token",
    join_key="session_id"
)
