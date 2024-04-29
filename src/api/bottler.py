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
        red_sum = connection.execute(sqlalchemy.text("SELECT SUM(red_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.red_ml - 100 * :sum"), [{"sum": red_sum}])
        red_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 1")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_red WHERE id = 1"), [{"new_red": red_sum + red_cur}])

        green_sum = connection.execute(sqlalchemy.text("SELECT SUM(green_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.green_ml - 100 * :sum"), [{"sum": green_sum}])
        green_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 2")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_green WHERE id = 2"), [{"new_green": green_sum + green_cur}])

        blue_sum = connection.execute(sqlalchemy.text("SELECT SUM(blue_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.blue_ml - 100 * :sum"), [{"sum": blue_sum}])
        blue_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 3")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_blue WHERE id = 3"), [{"new_blue": blue_sum + blue_cur}])

        brown_sum = connection.execute(sqlalchemy.text("SELECT SUM(brown_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.red_ml - 50 * :sum"), [{"sum": brown_sum}])
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.green_ml - 50 * :sum"), [{"sum": brown_sum}])
        brown_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 4")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_brown WHERE id = 4"), [{"new_brown": brown_sum + brown_cur}])

        teal_sum = connection.execute(sqlalchemy.text("SELECT SUM(teal_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.green_ml - 50 * :sum"), [{"sum": teal_sum}])
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.blue_ml - 50 * :sum"), [{"sum": teal_sum}])
        teal_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 5")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_teal WHERE id = 5"), [{"new_teal": teal_sum + teal_cur}])

        purple_sum = connection.execute(sqlalchemy.text("SELECT SUM(purple_change) FROM potion_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.red_ml - 50 * :sum"), [{"sum": purple_sum}])
        connection.execute(sqlalchemy.text("UPDATE resources SET quantity = resources.blue_ml - 50 * :sum"), [{"sum": purple_sum}])
        purple_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 6")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_purple WHERE id = 6"), [{"new_purple": purple_sum + purple_cur}])

        connection.execute(sqlalchemy.text("TRUNCATE potion_ledgers"))

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
        red_ml, green_ml, blue_ml = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml FROM resources")).first()
        # Add different potions to the plan
        while(red_ml >= 50 or green_ml >= 50 or blue_ml >= 50):
            if(red_ml >= 50 and green_ml >= 50):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 0, "blue": 0, "green": 0, "purple": 0, "teal": 0, "brown": 1}])
                plan.append({
                    "potion_type": [50, 50, 0, 0],
                    "quantity": 1
                })
                red_ml -= 50
                green_ml -= 50

            if(green_ml >= 50 and blue_ml >= 50):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 0, "blue": 0, "green": 0, "purple": 0, "teal": 1, "brown": 0}])
                plan.append({
                    "potion_type": [0, 50, 50, 0],
                    "quantity": 1
                })
                green_ml -= 50
                blue_ml -= 50
                
            if(red_ml >= 50 and blue_ml >= 50):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 0, "blue": 0, "green": 0, "purple": 1, "teal": 0, "brown": 0}])
                plan.append({
                    "potion_type": [50, 0, 50, 0],
                    "quantity": 1
                })
                red_ml -= 50
                blue_ml -= 50

            if(red_ml >= 100):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 1, "blue": 0, "green": 0, "purple": 0, "teal": 0, "brown": 0}])
                plan.append({
                    "potion_type": [100, 0, 0, 0],
                    "quantity": 1
                })
                red_ml -= 100

            if(green_ml >= 100):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 0, "blue": 0, "green": 1, "purple": 0, "teal": 0, "brown": 0}])
                plan.append({
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1
                })
                green_ml -= 100

            if(blue_ml >= 100):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (red_change, green_change, blue_change, purple_change, teal_change, brown_change) VALUES (:red, :green, :blue, :purple, :teal, :brown)"), [{"red": 0, "blue": 1, "green": 0, "purple": 0, "teal": 0, "brown": 0}])
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
