from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    with db.engine.begin() as connection:
        for potion in potions_delivered:

            # Remove green ml
            potions_ml = potion.quantity * 100
            cur_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + (cur_green_ml - potions_ml)))

            # Add green potions
            cur_potion_quantity = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
            cur_potion_quantity += potion.quantity
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + cur_potion_quantity))

    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Bottle potions
    with db.engine.begin() as connection:
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        while green_ml >= 100:
            green_ml -= 100
            green_potions += 1

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions. (changed to green potions)

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
