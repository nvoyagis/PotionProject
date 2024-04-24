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
        potion_list = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock")).all()
        num_of_pots = potion_list[0][0] + potion_list[1][0] + potion_list[2][0] + potion_list[3][0] + potion_list[4][0] + potion_list[5][0]
        ml_list = connection.execute(sqlalchemy.text("SELECT * FROM resources")).all()
        total_ml = ml_list[0][1] + ml_list[0][2] + ml_list[0][3]
        num_of_gold = connection.execute(sqlalchemy.text("SELECT gold FROM extra_resources")).scalar_one()
    return {"number_of_potions": num_of_pots, "ml_in_barrels": total_ml, "gold": num_of_gold}

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
