from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    with db.engine.begin() as connection:
        # Defensive programming (helps identify bugs)
        #for barrel in barrels_delivered:
            #if barrel.potion_type != [1, 0, 0, 0] and barrel.potion_type != [0, 1, 0, 0] and barrel.potion_type != [0, 0, 1, 0]:
                #raise Exception("Invalid potion type")


        # Combine ledgers and remove them
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = (SELECT SUM(red_change) FROM resource_ledgers) + resources.red_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = (SELECT SUM(green_change) FROM resource_ledgers) + resources.green_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = (SELECT SUM(blue_change) FROM resource_ledgers) + resources.blue_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET gold = (SELECT SUM(gold_change) FROM resource_ledgers) + resources.gold"))
            connection.execute(sqlalchemy.text("TRUNCATE resource_ledgers"))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # Purchase barrels
    with db.engine.begin() as connection:
        json = []
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM resources")).scalar_one()
        red, green, blue = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml FROM resources")).first()
        
        avg = (red + green + blue)/3

        if red > avg:
            r = random.randint(0,1)
        else:
            r = 0
        if green > avg:
            g = random.randint(0,1)
        else:
            g = 0
        if blue > avg:
            b = random.randint(0,1)
        else:
            b = 0

        for barrel in wholesale_catalog:
            r = random.randint(0,2)
            quantity = barrel.quantity
            purchase_quantity = 0

            if barrel.price <=  gold and r == 0 and barrel.potion_type == [1, 0, 0, 0]: 
                while quantity > 0 and barrel.price <= gold:
                    gold -= barrel.price
                    quantity -= 1
                    purchase_quantity += 1
                connection.execute(sqlalchemy.text("INSERT INTO resource_ledgers (red_change, green_change, blue_change, dark_change, gold_change) VALUES (:red, :green, :blue, :dark, :gold)"), [{"red": barrel.ml_per_barrel * purchase_quantity, "green": 0, "blue": 0, "dark": 0, "gold": -barrel.price * purchase_quantity}])
                json.append({
                    "sku": barrel.sku,
                    "quantity": purchase_quantity
                })
                
            elif barrel.price <= gold and g == 0 and barrel.potion_type == [0, 1, 0, 0]: 
                while quantity > 0 and barrel.price <= gold:
                    gold -= barrel.price
                    quantity -= 1
                    purchase_quantity += 1
                connection.execute(sqlalchemy.text("INSERT INTO resource_ledgers (red_change, green_change, blue_change, dark_change, gold_change) VALUES (:red, :green, :blue, :dark, :gold)"), [{"red": 0, "green": barrel.ml_per_barrel * purchase_quantity, "blue": 0, "dark": 0, "gold": -barrel.price * purchase_quantity}])
                json.append({
                    "sku": barrel.sku,
                    "quantity": purchase_quantity
                })

            elif barrel.price <= gold and b == 0 and barrel.potion_type == [0, 0, 1, 0]: 
                while quantity > 0 and barrel.price <= gold:
                    gold -= barrel.price
                    quantity -= 1
                    purchase_quantity += 1
                connection.execute(sqlalchemy.text("INSERT INTO resource_ledgers (red_change, green_change, blue_change, dark_change, gold_change) VALUES (:red, :green, :blue, :dark, :gold)"), [{"red": 0, "green": 0, "blue": barrel.ml_per_barrel * purchase_quantity, "dark": 0, "gold": -barrel.price * purchase_quantity}])
                json.append({
                    "sku": barrel.sku,
                    "quantity": purchase_quantity
                })
            
            elif barrel.price <= gold and barrel.potion_type == [0, 0, 0, 1]:
                while quantity > 0 and barrel.price <= gold:
                    gold -= barrel.price
                    quantity -= 1
                    purchase_quantity += 1
                connection.execute(sqlalchemy.text("INSERT INTO resource_ledgers (red_change, green_change, blue_change, dark_change, gold_change) VALUES (:red, :green, :blue, :dark, :gold)"), [{"red": 0, "green": 0, "blue": 0, "dark": barrel.ml_per_barrel * purchase_quantity, "gold": -barrel.price * purchase_quantity}])
                json.append({
                    "sku": barrel.sku,
                    "quantity": purchase_quantity
                })
            

    return json
