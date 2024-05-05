from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

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
            
        # Get all sums of potion ledgers
        red, green, blue, brown, purple, dark_red, dark_green, dark_blue, dark_brown, dark_purple, dark, white = connection.execute(sqlalchemy.text("""SELECT SUM(red_change), SUM(green_change), SUM(blue_change), 
                                                                                                                                                    SUM(brown_change), SUM(purple_change), SUM(dark_red_change), 
                                                                                                                                                    SUM(dark_green_change), SUM(dark_blue_change), SUM(dark_brown_change), 
                                                                                                                                                    SUM(dark_purple_change), SUM(dark_change), SUM(white_change) FROM potion_ledgers""")).first()
        
        # Remove ledgers
        connection.execute(sqlalchemy.text("TRUNCATE potion_ledgers"))
        
        # Remove used resources and add potions to potion_stock
        connection.execute(sqlalchemy.text("""UPDATE resources SET red_ml = resources.red_ml - :red_sum * 100 - :purple_sum * 50 - :brown_sum * 50 - :dark_red_sum * 80 - :dark_brown_sum * 40 - :dark_purple_sum * 40 - :white_sum * 34,
                                              green_ml = resources.green_ml - :green_sum * 100 - :brown_sum * 50 - :dark_green_sum * 80 - :dark_brown_sum * 40 - :white_sum * 33, 
                                              blue_ml = resources.blue_ml - :blue_sum * 100 - :purple_sum * 50 - :dark_blue_sum * 80 - :dark_purple_sum * 40 - :white_sum * 33,
                                              dark_ml = resources.dark_ml - :dark_sum * 100 - :dark_red_sum * 20 - :dark_green_sum * 20 - :dark_blue_sum * 20 - :dark_purple_sum * 20 - :dark_brown_sum * 20
                                           """), [{"red_sum": int(red), "green_sum": int(green), "blue_sum": int(blue), "brown_sum": int(brown), "purple_sum": int(purple), "dark_green_sum": int(dark_green), "dark_blue_sum": int(dark_blue), "dark_red_sum": int(dark_red), "dark_brown_sum": int(dark_brown), "dark_purple_sum": int(dark_purple), "dark_sum": int(dark), "white_sum": int(white)}])
                                              
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :red_sum WHERE id = 1"), [{"red_sum": int(red),}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :green_sum WHERE id = 2"), [{"green_sum": int(green)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :blue_sum WHERE id = 3"), [{"blue_sum": int(blue)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :brown_sum WHERE id = 4"), [{"brown_sum": int(brown)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :purple_sum WHERE id = 6"), [{"purple_sum": int(purple)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_red_sum WHERE id = 7"), [{"dark_red_sum": int(dark_red)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_green_sum WHERE id = 8"), [{"dark_green_sum": int(dark_green)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_blue_sum WHERE id = 9"), [{"dark_blue_sum": int(dark_blue)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_brown_sum WHERE id = 10"), [{"dark_brown_sum": int(dark_brown)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_purple_sum WHERE id = 12"), [{"dark_purple_sum": int(dark_purple)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :dark_sum WHERE id = 13"), [{"dark_sum": int(dark)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity + :white_sum WHERE id = 14"), [{"white_sum": int(white)}])

        print(f"potions delivered: {potions_delivered} order_id: {order_id}")

        return "OK"
    
    
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Return all potions

    
    # Begin potion order
    order = []

    with db.engine.begin() as connection:

        # Get all current resource values.
        red_ml, green_ml, blue_ml, dark_ml = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml FROM resources")).first()
        resource_list = [red_ml, green_ml, blue_ml, dark_ml]

        avg = (red_ml + green_ml + blue_ml)/3

        r = 1
        g = 1
        b = 1
        
        # Add different potions to the plan.
        while(red_ml >= 100 or green_ml >= 100 or blue_ml >= 100):

            # 50% chance of using low-ml colors for each loop. 100% chance of using high-ml colors.
            if red_ml < avg:
                r = random.randint(0,1)
            if green_ml < avg:
                g = random.randint(0,1)
            if blue_ml < avg:
                b = random.randint(0,1)

            potion_question_mark = False

            potion_info = connection.execute(sqlalchemy.text("SELECT type, price FROM potion_stock"))
            
            # Cycle through each potion type.
            for potion in potion_info:
                bottling = True
                bottled_potions = 0

                # Loop through a potion that can be bottled
                while bottling:

                    # Cycle through each ingredient.
                    for i in range(4):
                    
                        # Checks if there are enough resources to make a given potion.
                        if resource_list[i] < potion.type[i]:
                            bottling = False
                            break
                    
                    # End a specific potion's loop if a potion can't be bottled.
                    if bottling is False:
                        break

                    # Remove resources needed to make a given potion.
                    for i in range(4):
                        resource_list[i] -= potion.type[i]

                    # Bottle a potion.
                    bottled_potions += 1

                    # Help bottle potions without wasting too many resources. Incorporate RNG with the resources that are being used to help bottle a variety of potions.
                    if potion.type[0] != 0 and 1.2 * red_ml < avg:
                        r = random.randint(0,1)
                    if potion.type[1] != 0 and 1.2 * green_ml < avg:
                        g = random.randint(0,1)
                    if potion.type[2] != 0 and 1.2 * blue_ml < avg:
                        b = random.randint(0,1)
                    
                    # End loop if a used color is "unlucky" and its amount is relatively low.
                    if r == 0 or g == 0 or b == 0:
                        break
                
                # Add bottled potions to the order.
                if bottled_potions != 0:
                    order.append({
                    "potion_type": [80, 0, 0, 20],
                    "quantity": 1
                })
            
        # Submit finished order
        return order
    

if __name__ == "__main__":
    print(get_bottle_plan())
