from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE resources SET red_ml = 0"))
        connection.execute(sqlalchemy.text("UPDATE resources SET green_ml = 0"))
        connection.execute(sqlalchemy.text("UPDATE resources SET blue_ml = 0"))
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = 0"))
        connection.execute(sqlalchemy.text("UPDATE extra_resources SET gold = 100"))
        connection.execute(sqlalchemy.text("UPDATE extra_resources SET dark_ml = 0"))
        connection.execute(sqlalchemy.text("DELETE FROM carts_and_customers"))
        connection.execute(sqlalchemy.text("DELETE FROM carts_and_items"))

    return "OK"

