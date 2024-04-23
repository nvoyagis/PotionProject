from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        item_list = []
        # Store sku & quantity of each potion in a CursorResult
        potion_info = connection.execute(sqlalchemy.text("SELECT quantity, sku, name, type, price FROM potion_stock"))
        
        # Get data from CursorResult
        for row in potion_info:
            if row.quantity != 0:
                item_list.append({
                    "sku": row.sku,
                    "name": row.name,
                    "quantity": row.quantity,
                    "price": row.price,
                    "potion_type": row.type
                })
            
        return item_list