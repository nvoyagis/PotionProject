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
        # Defensive programming! (helps identify bugs)
        for barrel in barrels_delivered:
            if barrel.potion_type != [1, 0, 0, 0] and barrel.potion_type != [0, 1, 0, 0] and barrel.potion_type != [0, 0, 1, 0]:
                raise Exception("Invalid potion type")


        # Combine ledgers and remove them
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = (SELECT SUM(red_change) FROM resources_ledgers) + resources.red_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = (SELECT SUM(green_change) FROM resources_ledgers) + resources.green_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = (SELECT SUM(blue_change) FROM resources_ledgers) + resources.blue_ml"))
            connection.execute(sqlalchemy.text("UPDATE resources SET gold = (SELECT SUM(gold_change) FROM resources_ledgers) + resources.gold"))
            connection.execute(sqlalchemy.text("TRUNCATE resources"))





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
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)"), [{"red": barrel.ml_per_barrel, "blue": 0, "green": 0, "gold": -barrel.price}])
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })
                
            elif barrel.price <= gold and r == 1 and barrel.potion_type == [0, 1, 0, 0]: 
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)"), [{"red": 0, "blue": barrel.ml_per_barrel, "green": 0, "gold": -barrel.price}])
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })

            elif barrel.price <= gold and r == 2 and barrel.potion_type == [0, 0, 1, 0]: 
                connection.execute(sqlalchemy.text("INSERT INTO resources_ledgers (red_change, green_change, blue_change, gold_change) VALUES (:red, :green, :blue, :gold)"), [{"red": 0, "blue": 0, "green": barrel.ml_per_barrel, "gold": -barrel.price}])
                gold -= barrel.price
                json.append({
                    "sku": barrel.sku,
                    "quantity": 1
                })
            

    return json
