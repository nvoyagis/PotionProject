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
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        # Add ledgers for ml and gold spent
        for barrel in barrels_delivered:
            if barrel.potion_type == [1, 0, 0 , 0]:
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)")[{"red": barrel.ml_per_barrel, "blue": 0, "green": 0, "gold": -barrel.price}])
            elif barrel.potion_type == [0, 1, 0 , 0]:
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)")[{"red": 0, "blue": barrel.ml_per_barrel, "green": 0, "gold": -barrel.price}])
            elif barrel.potion_type == [0, 0, 1 , 0]:
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)")[{"red": 0, "blue": 0, "green": barrel.ml_per_barrel, "gold": -barrel.price}])

            # Defensive programming! (helps identify bugs)
            else:
                raise Exception("Invalid potion type")


        # Combine ledgers... Must add them to resources table later
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)")[{"red": red_ml, "blue": blue_ml, "green": green_ml, "gold": cost}])
            connection.execute(sqlalchemy.text("SELECT SUM(red_change) AS red_ml FROM resources_ledgers WHERE blue_change = 0, green_change = 0"))
            connection.execute(sqlalchemy.text("SELECT SUM(green_change) AS green_ml FROM resources_ledgers WHERE red_change = 0, blue_change = 0"))
            connection.execute(sqlalchemy.text("SELECT SUM(blue_change) AS blue_ml FROM resources_ledgers WHERE red_change = 0, green_change = 0"))
    return "OK"

# Gets called once a day, v1
# Make min & max thresholds
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # Purchase barrels
    with db.engine.begin() as connection:
        json = []
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM resources")).scalar_one()
        for barrel in wholesale_catalog:
            r = random.randint(0,2)
            if barrel.price <= gold and r == 0 and barrel.potion_type == [1, 0, 0, 0]: 
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })
                
            elif barrel.price <= gold and r == 1 and barrel.potion_type == [0, 1, 0, 0]: 
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })

            elif barrel.price <= gold and r == 2 and barrel.potion_type == [0, 0, 1, 0]: 
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })

    return json
