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
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    sum_price = 0

    # Add RBG ml & find total price
    for barrel in barrels_delivered:
        if barrel.potion_type == [1, 0, 0 , 0]:
            red_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0, 1, 0 , 0]:
            green_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0, 0, 1 , 0]:
            blue_ml += barrel.ml_per_barrel * barrel.quantity

        sum_price += barrel.price

    # Set new amount of gold & RGB ml
    with db.engine.begin() as connection:
        cur_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
        cur_gold -= sum_price

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = " + str(red_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + str(green_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = " + str(blue_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(cur_gold)))

    return "OK"

# Gets called once a day, v1
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # Purchase a barrel if the number of green potions is less than 10 and it can be afforded
    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
        for barrel in wholesale_catalog:
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
            if barrel.price <= gold and num_red_potions < 10 and barrel.potion_type == [1, 0, 0, 0]: 
                return [
                {
                    "sku": barrel.sku,
                    "quantity": 1
                }
                ]
            if barrel.price <= gold and num_green_potions < 10 and barrel.potion_type == [0, 1, 0, 0]: 
                return [
                {
                    "sku": barrel.sku,
                    "quantity": 1
                }
                ]
            if barrel.price <= gold and num_blue_potions < 10 and barrel.potion_type == [0, 0, 1, 0]: 
                return [
                {
                    "sku": barrel.sku,
                    "quantity": 1
                }
            ]

    return []
