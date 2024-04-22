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

            # Remove RGB ml and add RGB potions
            if potion.potion_type == [100, 0, 0, 0]:
                red_ml = potion.quantity * 100
                cur_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = " + str(cur_red_ml - red_ml)))

                cur_red_quantity = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
                cur_red_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(cur_red_quantity)))

            elif potion.potion_type == [0, 100, 0, 0]:
                green_ml = potion.quantity * 100
                cur_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + str(cur_green_ml - green_ml)))

                cur_green_quantity = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
                cur_green_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + str(cur_green_quantity)))

            elif potion.potion_type == [0, 0, 100, 0]:
                blue_ml = potion.quantity * 100
                cur_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = " + str(cur_blue_ml - blue_ml)))

                cur_blue_quantity = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
                cur_blue_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = " + str(cur_blue_quantity)))

    # Make 1 of each potion that's possible to make (while updating the resources used)







    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Bottle RGB potions
    
    plan = []

    with db.engine.begin() as connection:
        # Make an array that contains tuples for each color (in ml) that I have and then another array for the types of potions being sold
        colors = connection.execute(sqlalchemy.text("SELECT * FROM resources")).first()
        for color in colors:
            
            # Add different potions to the plan
            if(color[0] >= 50 and color[1] >= 50):
                plan.append({
                    "potion_type": [50, 50, 0, 0],
                    "quantity": 1
                })
                color[50] -= 50
                color[50] -= 50

            if(color[1] >= 50 and color[2] >= 50):
                plan.append({
                    "potion_type": [0, 50, 50, 0],
                    "quantity": 1
                })
                color[1] -= 50
                color[2] -= 50
            
            if(color[0] >= 50 and color[2] >= 50):
                plan.append({
                    "potion_type": [50, 0, 50, 0],
                    "quantity": 1
                })
                color[0] -= 50
                color[2] -= 50

            if(color[0] >= 100):
                plan.append({
                    "potion_type": [100, 0, 0, 0],
                    "quantity": 1
                })
                color[0] -= 100

            if(color[1] >= 100):
                plan.append({
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1
                })
                color[1] -= 100

            if(color[2] >= 100):
                plan.append({
                    "potion_type": [0, 0, 100, 0],
                    "quantity": 1
                })
                color[2] -= 100
        
        return plan








    with db.engine.begin() as connection:
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        red_potions = 0
        while red_ml >= 100:
            red_ml -= 100
            red_potions += 1

        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        green_potions = 0
        while green_ml >= 100:
            green_ml -= 100
            green_potions += 1

        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        blue_potions = 0
        while blue_ml >= 100:
            blue_ml -= 100
            blue_potions += 1

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Return all potions
    
    if red_potions != 0 and green_potions != 0 and blue_potions != 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions
            }
        ]
    
    elif red_potions == 0 and green_potions != 0 and blue_potions != 0:
        return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions
            }
        ]
    
    elif red_potions != 0 and green_potions == 0 and blue_potions != 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions
            }
        ]
    
    elif red_potions != 0 and green_potions != 0 and blue_potions == 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions
            }
        ]

    elif red_potions == 0 and green_potions == 0 and blue_potions != 0:
        return [
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions
            }
        ]
    
    elif red_potions == 0 and green_potions != 0 and blue_potions == 0:
        return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions
            }
        ]
    
    elif red_potions != 0 and green_potions == 0 and blue_potions == 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions
            }
        ]
    
    return []

if __name__ == "__main__":
    print(get_bottle_plan())
