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

            # Remove ml and add potions
            if potion.potion_type == [100, 0, 0, 0]:
                red_ml = potion.quantity * 100
                cur_red_ml = connection.execute(sqlalchemy.text("SELECT red_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = " + str(cur_red_ml - red_ml)))

                cur_red_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 1")).scalar_one()
                cur_red_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_red_quantity) + " WHERE id = 1"))


            elif potion.potion_type == [0, 100, 0, 0]:
                green_ml = potion.quantity * 100
                cur_green_ml = connection.execute(sqlalchemy.text("SELECT green_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = " + str(cur_green_ml - green_ml)))

                cur_green_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 2")).scalar_one()
                cur_green_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_green_quantity) + " WHERE id = 2"))


            elif potion.potion_type == [0, 0, 100, 0]:
                blue_ml = potion.quantity * 100
                cur_blue_ml = connection.execute(sqlalchemy.text("SELECT blue_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = " + str(cur_blue_ml - blue_ml)))

                cur_blue_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 3")).scalar_one()
                cur_blue_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_blue_quantity) + " WHERE id = 3"))

            elif potion.potion_type == [50, 50, 0, 0]:
                red_ml = potion.quantity * 50
                cur_red_ml = connection.execute(sqlalchemy.text("SELECT red_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = " + str(cur_red_ml - red_ml)))

                green_ml = potion.quantity * 50
                cur_green_ml = connection.execute(sqlalchemy.text("SELECT green_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = " + str(cur_green_ml - green_ml)))

                cur_brown_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 4")).scalar_one()
                cur_brown_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_brown_quantity) + " WHERE id = 4"))

            elif potion.potion_type == [0, 50, 50, 0]:
                green_ml = potion.quantity * 50
                cur_green_ml = connection.execute(sqlalchemy.text("SELECT green_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = " + str(cur_green_ml - green_ml)))

                blue_ml = potion.quantity * 50
                cur_blue_ml = connection.execute(sqlalchemy.text("SELECT blue_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = " + str(cur_blue_ml - blue_ml)))

                cur_teal_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 5")).scalar_one()
                cur_teal_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_teal_quantity) + " WHERE id = 5"))

            elif potion.potion_type == [50, 0, 50, 0]:
                red_ml = potion.quantity * 50
                cur_red_ml = connection.execute(sqlalchemy.text("SELECT red_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = " + str(cur_red_ml - red_ml)))

                blue_ml = potion.quantity * 50
                cur_blue_ml = connection.execute(sqlalchemy.text("SELECT blue_ml FROM resources")).scalar_one()
                connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = " + str(cur_blue_ml - blue_ml)))

                cur_purple_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock WHERE id = 6")).scalar_one()
                cur_purple_quantity += potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = " + str(cur_purple_quantity) + " WHERE id = 6"))

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
        red_ml, green_ml, blue_ml = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml FROM resources")).first()
        # Add different potions to the plan
        while(red_ml >= 50 and green_ml >= 50 and blue_ml >= 50):
            if(red_ml >= 50 and green_ml >= 50):
                plan.append({
                    "potion_type": [50, 50, 0, 0],
                    "quantity": 1
                })
                red_ml -= 50
                green_ml -= 50

            if(green_ml >= 50 and blue_ml >= 50):
                plan.append({
                    "potion_type": [0, 50, 50, 0],
                    "quantity": 1
                })
                green_ml -= 50
                blue_ml -= 50
                
            if(red_ml >= 50 and blue_ml >= 50):
                plan.append({
                    "potion_type": [50, 0, 50, 0],
                    "quantity": 1
                })
                red_ml -= 50
                blue_ml -= 50

            if(red_ml >= 100):
                plan.append({
                    "potion_type": [100, 0, 0, 0],
                    "quantity": 1
                })
                red_ml -= 100

            if(green_ml >= 100):
                plan.append({
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1
                })
                green_ml -= 100

            if(blue_ml >= 100):
                plan.append({
                    "potion_type": [0, 0, 100, 0],
                    "quantity": 1
                })
                blue_ml -= 100
        
        return plan



    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Return all potions
    

if __name__ == "__main__":
    print(get_bottle_plan())
