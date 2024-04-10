from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        num_red_pots = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        num_green_pots = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        num_blue_pots = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
        num_of_pots = num_red_pots + num_green_pots + num_blue_pots
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        num_of_ml = num_red_ml + num_green_ml + num_blue_ml
        num_of_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
    return {"number_of_potions": num_of_pots, "ml_in_barrels": num_of_ml, "gold": num_of_gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
