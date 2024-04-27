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

@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text("INSERT INTO carts_and_customers (name, class, level) VALUES ('" + new_cart.customer_name + "', '" + new_cart.character_class + "', '" + str(new_cart.level) + "') RETURNING id")).scalar_one()
    return {"cart_id": id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts_and_items (id, quantity, sku) VALUES ('" + str(cart_id) + "', '" + str(cart_item.quantity) + "', '" + item_sku + "')"))
        potion_price = connection.execute(sqlalchemy.text("SELECT price FROM potion_stock WHERE sku = :ordersku"), [{"ordersku": item_sku}]).scalar_one()
        price = int(potion_price) * cart_item.quantity
        if item_sku == "RED_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, red_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])
        elif item_sku == "GREEN_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, green_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])
        elif item_sku == "BLUE_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, blue_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])
        elif item_sku == "PURPLE_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, purple_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])
        elif item_sku == "BROWN_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, brown_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])
        elif item_sku == "TEAL_POTION_0":
            connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, teal_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity}])

    return "OK"

# payment is not amount of gold apparently
class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:

        red_sum = connection.execute(sqlalchemy.text("SELECT SUM(red_change) FROM cart_ledgers")).scalar_one()
        red_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 1")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_red WHERE id = 1"), [{"new_red": red_sum + red_cur}])

        green_sum = connection.execute(sqlalchemy.text("SELECT SUM(green_change) FROM cart_ledgers")).scalar_one()
        green_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 2")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_green WHERE id = 2"), [{"new_green": green_sum + green_cur}])

        blue_sum = connection.execute(sqlalchemy.text("SELECT SUM(blue_change) FROM cart_ledgers")).scalar_one()
        blue_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 3")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_blue WHERE id = 3"), [{"new_blue": blue_sum + blue_cur}])

        brown_sum = connection.execute(sqlalchemy.text("SELECT SUM(brown_change) FROM cart_ledgers")).scalar_one()
        brown_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 4")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_brown WHERE id = 4"), [{"new_brown": brown_sum + brown_cur}])

        teal_sum = connection.execute(sqlalchemy.text("SELECT SUM(teal_change) FROM cart_ledgers")).scalar_one()
        teal_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 5")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_teal WHERE id = 5"), [{"new_teal": teal_sum + teal_cur}])

        purple_sum = connection.execute(sqlalchemy.text("SELECT SUM(purple_change) FROM cart_ledgers")).scalar_one()
        purple_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 6")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_purple WHERE id = 6"), [{"new_purple": purple_sum + purple_cur}])

        gold_sum = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM cart_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET gold = :goldsum + resources.gold"), [{"goldsum": gold_sum}])

        connection.execute(sqlalchemy.text("TRUNCATE cart_ledgers"))


        # Get quantity and sku using cart_id in carts_and_items
        order_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM carts_and_items WHERE id = " + str(cart_id))).first()
        print(order_quantity)

        # Return purhcase info
        return {"total_potions_bought": order_quantity, "total_gold_paid": gold_sum}