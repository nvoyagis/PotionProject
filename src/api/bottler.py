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

            # Remove RGB color
            if potion.potion_type == [100, 0, 0, 0]:
                red_ml = potion.quantity * 100
                cur_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = " + str(cur_red_ml - red_ml)))
            elif potion.potion_type == [0, 100, 0, 0]:
                green_ml = potion.quantity * 100
                cur_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + str(cur_green_ml - green_ml)))
            elif potion.potion_type == [0, 0, 100, 0]:
                blue_ml = potion.quantity * 100
                cur_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = " + str(cur_blue_ml - blue_ml)))

            # Add RGB potions
            cur_red_quantity = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
            cur_red_quantity += potion.quantity
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(cur_red_quantity)))
            cur_green_quantity = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
            cur_green_quantity += potion.quantity
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + str(cur_green_quantity)))
            cur_blue_quantity = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
            cur_blue_quantity += potion.quantity
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = " + str(cur_blue_quantity)))

    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Bottle RGB potions
    with db.engine.begin() as connection:
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        while red_ml >= 100:
            red_ml -= 100
            red_potions += 1

        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        while green_ml >= 100:
            green_ml -= 100
            green_potions += 1

        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
        while blue_ml >= 100:
            blue_ml -= 100
            blue_potions += 1

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Return all potions
    

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions,
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions,
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
