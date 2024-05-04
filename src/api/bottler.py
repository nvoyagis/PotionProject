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
                                              UPDATE resources SET green_ml = resources.green_ml - :green_sum * 100 - :brown_sum * 50 - :dark_green_sum * 80 - :dark_brown_sum * 40 - :white_sum * 33, 
                                              UPDATE resources SET blue_ml = resources.blue_ml - :blue_sum * 100 - :purple_sum * 50 - :dark_blue_sum * 80 - :dark_purple_sum * 40 - :white_sum * 33,
                                              UPDATE resources SET dark_ml = resources.dark_ml - :dark_sum * 100 - :dark_red_sum * 20 - :dark_green_sum * 20 - :dark_blue_sum * 20 - :dark_purple_sum * 20 - :dark_brown_sum * 20,
                                              UPDATE potion_stock SET quantity = :red_sum WHERE id = 1,
                                              UPDATE potion_stock SET quantity = :green_sum WHERE id = 2,
                                              UPDATE potion_stock SET quantity = :blue_sum WHERE id = 3,
                                              UPDATE potion_stock SET quantity = :brown_sum WHERE id = 4,
                                              UPDATE potion_stock SET quantity = :purple_sum WHERE id = 6,
                                              UPDATE potion_stock SET quantity = :dark_red_sum WHERE id = 7,
                                              UPDATE potion_stock SET quantity = :dark_green_sum WHERE id = 8,
                                              UPDATE potion_stock SET quantity = :dark_blue_sum WHERE id = 9,
                                              UPDATE potion_stock SET quantity = :dark_brown_sum WHERE id = 10,
                                              UPDATE potion_stock SET quantity = :dark_purple_sum WHERE id = 12,
                                              UPDATE potion_stock SET quantity = :dark_sum WHERE id = 13,
                                              UPDATE potion_stock SET quantity = :white_sum WHERE id = 14
                                           """), [{"red_sum": int(red), "green_sum": int(green), "blue_sum": int(blue), "brown_sum": int(brown), "purple_sum": int(purple), "dark_green_sum": int(dark_green), "dark_blue_sum": int(dark_blue), "dark_red_sum": int(dark_red), "dark_brown_sum": int(dark_brown), "dark_purple_sum": int(dark_purple), "dark_sum": int(dark), "white_sum": int(white)}])

        print(f"potions delivered: {potions_delivered} order_id: {order_id}")

        return "OK"
    




        # Convert the CursorResult into a list of tuples
        potion_list = list(potion_ledgers.fetchall())

        # Add i'th value of each list in the CursorResult
        for i in range(potion_list.size() - 1):
            numpy.add(potion_list[i], ) 
        


            # Get ingredient list from potion name from a join w/ potion_info


        



        red_sum = connection.execute(sqlalchemy.text("SELECT SUM(red_change) FROM potion_ledgers")).scalar_one()
        if red_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 100 * :sum"), [{"sum": red_sum}])
            red_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 1")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_red WHERE id = 1"), [{"new_red": red_sum + red_cur}])

        green_sum = connection.execute(sqlalchemy.text("SELECT SUM(green_change) FROM potion_ledgers")).scalar_one()
        if green_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = resources.green_ml - 100 * :sum"), [{"sum": green_sum}])
            green_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 2")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_green WHERE id = 2"), [{"new_green": green_sum + green_cur}])

        blue_sum = connection.execute(sqlalchemy.text("SELECT SUM(blue_change) FROM potion_ledgers")).scalar_one()
        if blue_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = resources.blue_ml - 100 * :sum"), [{"sum": blue_sum}])
            blue_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 3")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_blue WHERE id = 3"), [{"new_blue": blue_sum + blue_cur}])

        brown_sum = connection.execute(sqlalchemy.text("SELECT SUM(brown_change) FROM potion_ledgers")).scalar_one()
        if brown_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 50 * :sum"), [{"sum": brown_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = resources.green_ml - 50 * :sum"), [{"sum": brown_sum}])
            brown_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 4")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_brown WHERE id = 4"), [{"new_brown": brown_sum + brown_cur}])

        purple_sum = connection.execute(sqlalchemy.text("SELECT SUM(purple_change) FROM potion_ledgers")).scalar_one()
        if purple_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 50 * :sum"), [{"sum": purple_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = resources.blue_ml - 50 * :sum"), [{"sum": purple_sum}])
            purple_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 6")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_purple WHERE id = 6"), [{"new_purple": purple_sum + purple_cur}])

        dark_red_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_red_change) FROM potion_ledgers")).scalar_one()
        if dark_red_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 80 * :sum"), [{"sum": dark_red_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 20 * :sum"), [{"sum": dark_red_sum}])
            dark_red_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 7")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark_red WHERE id = 7"), [{"new_dark_red": dark_red_sum + dark_red_cur}])

        dark_green_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_green_change) FROM potion_ledgers")).scalar_one()
        if dark_green_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = resources.green_ml - 80 * :sum"), [{"sum": dark_green_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 20 * :sum"), [{"sum": dark_green_sum}])
            dark_green_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 8")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark_green WHERE id = 8"), [{"new_dark_green": dark_green_sum + dark_green_cur}])

        dark_blue_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_blue_change) FROM potion_ledgers")).scalar_one()
        if dark_blue_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = resources.blue_ml - 80 * :sum"), [{"sum": dark_blue_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 20 * :sum"), [{"sum": dark_blue_sum}])
            dark_blue_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 9")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark_blue WHERE id = 9"), [{"new_dark_blue": dark_blue_sum + dark_blue_cur}])

        dark_brown_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_brown_change) FROM potion_ledgers")).scalar_one()
        if dark_brown_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 40 * :sum"), [{"sum": dark_brown_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = resources.green_ml - 40 * :sum"), [{"sum": dark_brown_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 20 * :sum"), [{"sum": dark_brown_sum}])
            dark_brown_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 10")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark_brown WHERE id = 10"), [{"new_dark_brown": dark_brown_sum + dark_brown_cur}]) 
        
        dark_purple_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_purple_change) FROM potion_ledgers")).scalar_one()
        if dark_purple_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 40 * :sum"), [{"sum": dark_purple_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = resources.blue_ml - 40 * :sum"), [{"sum": dark_purple_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 20 * :sum"), [{"sum": dark_purple_sum}])
            dark_purple_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 12")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark_purple WHERE id = 12"), [{"new_dark_purple": dark_purple_sum + dark_purple_cur}]) 

        dark_sum = connection.execute(sqlalchemy.text("SELECT SUM(dark_change) FROM potion_ledgers")).scalar_one()
        if dark_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET dark_ml = resources.dark_ml - 100 * :sum"), [{"sum": dark_sum}])
            dark_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 13")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_dark WHERE id = 13"), [{"new_dark": dark_sum + dark_cur}]) 

        white_sum = connection.execute(sqlalchemy.text("SELECT SUM(white_change) FROM potion_ledgers")).scalar_one()
        if white_sum != 0:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = resources.red_ml - 34 * :sum"), [{"sum": white_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = resources.blue_ml - 33 * :sum"), [{"sum": white_sum}])
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = resources.green_ml - 33 * :sum"), [{"sum": white_sum}])
            white_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 14")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_white WHERE id = 14"), [{"new_white": white_sum + white_cur}]) 

        connection.execute(sqlalchemy.text("TRUNCATE potion_ledgers"))

        print(f"potions delivered: {potions_delivered} order_id: {order_id}")

        return "OK"
    
    
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
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








                    

            if(red_ml >= 50 and green_ml >= 50 and r == 1 and g == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers brown_change VALUES 1"))
                plan.append({
                    "potion_type": [50, 50, 0, 0],
                    "quantity": 1
                })
                red_ml -= 50
                green_ml -= 50
                
            if(red_ml >= 50 and blue_ml >= 50 and r == 1 and b == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers purple_change VALUES 1"))
                plan.append({
                    "potion_type": [50, 0, 50, 0],
                    "quantity": 1
                })
                red_ml -= 50
                blue_ml -= 50

            if(red_ml >= 100 and r == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers red_change VALUES 1"))
                plan.append({
                    "potion_type": [100, 0, 0, 0],
                    "quantity": 1
                })
                red_ml -= 100

            if(green_ml >= 100 and g == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers green_change VALUES 1"))
                plan.append({
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1
                })
                green_ml -= 100

            if(blue_ml >= 100 and b == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers blue_change VALUES 1"))
                plan.append({
                    "potion_type": [0, 0, 100, 0],
                    "quantity": 1
                })
                blue_ml -= 100
            
            if(red_ml >= 80 and dark_ml >= 20 and r == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_red_change VALUES 1"))
                plan.append({
                    "potion_type": [80, 0, 0, 20],
                    "quantity": 1
                })
                red_ml -= 80
                dark_ml -= 20

            if(green_ml >= 80 and dark_ml >= 20 and g == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_green_change VALUES 1"))
                plan.append({
                    "potion_type": [0, 80, 0, 20],
                    "quantity": 1
                })
                green_ml -= 80
                dark_ml -= 20
            
            if(blue_ml >= 80 and dark_ml >= 20 and b == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_blue_change VALUES 1"))
                plan.append({
                    "potion_type": [0, 0, 80, 20],
                    "quantity": 1
                })
                blue_ml -= 80
                dark_ml -= 20

            if(red_ml >= 40 and green_ml >= 40 and dark_ml >= 20 and r == 1 and g == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_brown_change VALUES 1"))
                plan.append({
                    "potion_type": [40, 40, 0, 20],
                    "quantity": 1
                })
                red_ml -= 40
                green_ml -= 40
                dark_ml -= 20

            if(red_ml >= 40 and blue_ml >= 40 and dark_ml >= 20 and r == 1 and b == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_purple_change VALUES 1"))
                plan.append({
                    "potion_type": [40, 0, 40, 20],
                    "quantity": 1
                })
                blue_ml -= 40
                red_ml -= 40
                dark_ml -= 20

            if(dark_ml >= 100):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers dark_change VALUES 1"))
                plan.append({
                    "potion_type": [0, 0, 0, 100],
                    "quantity": 1
                })
                dark_ml -= 100

            if(red_ml >= 34 and blue_ml >= 33 and green_ml >= 33 and r == 1 and b == 1 and g == 1):
                potion_question_mark = True
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers white_change VALUES 1"))
                plan.append({
                    "potion_type": [34, 33, 33, 0],
                    "quantity": 1
                })
                red_ml -= 34
                green_ml -= 33
                blue_ml -= 33

            # End loop if no potions are made (maybe potions can be made but rng is unfavorable)
            if(potion_question_mark is False):
                break
        



    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Return all potions
    

if __name__ == "__main__":
    print(get_bottle_plan())
