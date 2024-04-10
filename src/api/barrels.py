from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
    green_ml = 0
    sum_price = 0

    for barrel in barrels_delivered:
        green_ml += barrel.ml_per_barrel * barrel.quantity
        sum_price += barrel.price

    # Set new amount of gold & green ml
    with db.engine.begin() as connection:
        cur_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
        cur_gold -= sum_price

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + green_ml))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + cur_gold))

    return "OK"

# Gets called once a day, v1
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # Purchase a barrel if the number of green potions is less than 10 and it can be afforded
    with db.engine.begin() as connection:
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        for barrel in wholesale_catalog:
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
            if barrel.price <= gold and num_green_potions < 10 and barrel.sku == "SMALL_GREEN_BARREL": 
                return [
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1,
                }
            ]

