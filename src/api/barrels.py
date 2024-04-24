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

    cost = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0

    # Add RBG ml & find total price. Use only 1 barrel b.c. only 1 type of barrel is purchased at a time.
    for barrel in barrels_delivered:
        if barrel.potion_type == [1, 0, 0 , 0]:
            red_ml += barrel.ml_per_barrel
        elif barrel.potion_type == [0, 1, 0 , 0]:
            green_ml += barrel.ml_per_barrel
        elif barrel.potion_type == [0, 0, 1 , 0]:
            blue_ml += barrel.ml_per_barrel
        # Defensive programming! (helps identify bugs)
        else:
            raise Exception("Invalid potion type")

        cost += barrel.price 

    # Set new amount of gold & RGB ml
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = " + "resources.red_ml + " + str(red_ml)))
        connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = " + "resources.green_ml + " + str(green_ml)))
        connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = " + "resources.blue_ml + " + str(blue_ml)))
        connection.execute(sqlalchemy.text("UPDATE extra_resources SET gold = " + "extra_resources.gold - " + str(cost)))

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
        for barrel in wholesale_catalog:
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM extra_resources")).scalar_one()
            r = random.randint(0,2)
            if barrel.price <= gold and r == 0 and barrel.potion_type == [1, 0, 0, 0]: 
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })
                
            elif barrel.price <= gold and r == 1 and barrel.potion_type == [0, 1, 0, 0]: 
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })

            elif barrel.price <= gold and r == 2 and barrel.potion_type == [0, 0, 1, 0]: 
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })

    return json
