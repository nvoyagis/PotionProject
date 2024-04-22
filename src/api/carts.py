from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"

unique_cart_id = 0
@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    global unique_cart_id
    unique_cart_id += 1
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts_and_customers (id, name, class, level) VALUES (" + str(unique_cart_id) + ", " + new_cart.customer_name + ", " + new_cart.character_class + ", " + str(new_cart.level) + ")"))
    return {"cart_id": unique_cart_id}


class CartItem(BaseModel):
    quantity: int

ids_and_carts = {}
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    global ids_and_carts
    ids_and_carts.update({cart_id: [cart_item.quantity, item_sku]})


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts_and_items (id, quantity, sku) VALUES (" + str(cart_id) + ", " + str(cart_item.quantity) + ", " + item_sku + ")"))
    return "OK"

# payment is not amount of gold apparently
class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:

        # Get quantity and sku using cart_id in carts_and_items
        purchase_info = connection.execute(sqlalchemy.text("SELECT * FROM carts_and_items WHERE id = " + str(cart_id))).all()

        # Get item info for payment using sku in potion_stock
        item_info = connection.execute(sqlalchemy.text("SELECT * FROM potion_stock WHERE sku = " + purchase_info[2])).all()

        # Update gold
        connection.execute(sqlalchemy.text("UPDATE extra_resources SET gold = " + "extra_resources.gold + " + str(purchase_info[1] * item_info[7])))

        # Update stock
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - " + str(purchase_info[1]) + " WHERE sku = " + item_info[6]))

        # Return purhcase info
        return {"total_potions_bought": purchase_info[1], "total_gold_paid": purchase_info[1] * item_info[7]}




        if ids_and_carts.get(cart_id)[1] == "RED_POTION_0":
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(cur_gold + 35 * ids_and_carts.get(cart_id)[0])))
            cur_red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(cur_red - ids_and_carts.get(cart_id)[0])))
            return {"total_potions_bought": ids_and_carts.get(cart_id)[0], "total_gold_paid": 35 * ids_and_carts.get(cart_id)[0]}
        elif ids_and_carts.get(cart_id)[1] == "GREEN_POTION_0":
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(cur_gold + 30 * ids_and_carts.get(cart_id)[0])))
            cur_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + str(cur_green - ids_and_carts.get(cart_id)[0])))
            return {"total_potions_bought": ids_and_carts.get(cart_id)[0], "total_gold_paid": 30 * ids_and_carts.get(cart_id)[0]}
        elif ids_and_carts.get(cart_id)[1] == "BLUE_POTION_0":
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(cur_gold + 28 * ids_and_carts.get(cart_id)[0])))
            cur_blue = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = " + str(cur_blue - ids_and_carts.get(cart_id)[0])))
            return {"total_potions_bought": ids_and_carts.get(cart_id)[0], "total_gold_paid": 28 * ids_and_carts.get(cart_id)[0]}
