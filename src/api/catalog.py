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
        num_red_pots = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        num_green_pots = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        num_blue_pots = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
    
        if num_red_pots !=0 or num_green_pots != 0 or num_blue_pots != 0:
            return [
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": num_red_pots,
                    "price": 25,
                    "potion_type": [100, 0, 0, 0],
                },
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num_green_pots,
                    "price": 30,
                    "potion_type": [0, 100, 0, 0],
                },
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": num_blue_pots,
                    "price": 35,
                    "potion_type": [0, 0, 100, 0],
                }
            ]
        return []
