from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        num_pots = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
    
    if num_pots >= 1:
        return [
                {
                  "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 10,
                    "potion_type": [0, 100, 0, 0],
                }
            ]
