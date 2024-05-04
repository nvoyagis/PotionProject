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

    if sort_col is search_sort_options.customer_name:
        order_by = db.carts_and_customers.c.name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.carts_and_items.c.sku
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.carts_and_items.c.quantity
    elif sort_col is search_sort_options.timestamp:
        order_by = db.carts_and_customers.c.time
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.carts_and_customers.c.name,
            db.carts_and_customers.c.title,
            db.movies.c.year,
            db.movies.c.imdb_rating,
            db.movies.c.imdb_votes,
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.movies.c.movie_id)
    )
    
    # make search_view in in SQLeditor
    # wanna use search_view to look at data... limit it... show specific qualities



    with db.engine.begin() as connection:

        connection.execute(sqlalchemy.text())

        customer_names = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY " + sort_col + " " + sort_order))
        quantities = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY " + sort_col + " " + sort_order))
        item_names = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY " + sort_col + " " + sort_order))


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
        id = connection.execute(sqlalchemy.text("INSERT INTO carts_and_customers (name, class, level) VALUES (:name, :class, :level) RETURNING id"), [{"name": new_cart.customer_name, "class": new_cart.character_class, "level": new_cart.level}]).scalar_one()
    return {"cart_id": id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    with db.engine.begin() as connection:

        # Insert a new order w/ item info
        connection.execute(sqlalchemy.text("INSERT INTO carts_and_items (id, quantity, sku) VALUES (:i, :q, :s)"), [{"i": cart_id, "q": cart_item.quantity, "s": item_sku}])

        # Get potion info and total price
        potion_price, potion_name = connection.execute(sqlalchemy.text("SELECT price, name FROM potion_stock WHERE sku = :ordersku"), [{"ordersku": item_sku}]).scalar_one()
        price = int(potion_price) * cart_item.quantity

        # Insert a potion new ledger
        connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, red_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity, "color": potion_name[-7] + "_change"}])


class CartCheckout(BaseModel):
    # Professor Pierce you are so funny for this
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        
        # Get all sums of cart ledgers
        red, green, blue, brown, purple, dark_red, dark_green, dark_blue, dark_brown, dark_purple, dark, white, gold_sum = connection.execute(sqlalchemy.text("""SELECT SUM(red_change), SUM(green_change), SUM(blue_change), 
                                                                                                                                                    SUM(brown_change), SUM(purple_change), SUM(dark_red_change), 
                                                                                                                                                    SUM(dark_green_change), SUM(dark_blue_change), SUM(dark_brown_change), 
                                                                                                                                                    SUM(dark_purple_change), SUM(dark_change), SUM(white_change), SUM(gold_change) FROM cart_ledgers""")).scalar_one()

        connection.execute(sqlalchemy.text("""UPDATE potion_stock SET quantity = potion_stock.quantity - :red_sum WHERE id = 1
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :green_sum WHERE id = 2
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :blue_sum WHERE id = 3
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :brown_sum WHERE id = 4
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :purple_sum WHERE id = 6
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_red_sum WHERE id = 7
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_green_sum WHERE id = 8
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_blue_sum WHERE id = 9
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_brown_sum WHERE id = 10 
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_purple_sum WHERE id = 12
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_sum WHERE id = 13
                                              UPDATE potion_stock SET quantity = potion_stock.quantity - :white_sum WHERE id = 14
                                              UPDATE resources SET gold = :goldsum + resources.gold
                                           """), [{"red_sum": red, "green_sum": green, "blue_sum": blue, "brown_sum": brown, "purple_sum": purple, "dark_green_sum": dark_green, "dark_blue_sum": dark_blue, "dark_red_sum": dark_red, "dark_brown_sum": dark_brown, "dark_purple_sum": dark_purple, "dark_sum": dark, "white_sum": white, "goldsum": gold_sum}])

        
        # Clear all cart ledgers
        connection.execute(sqlalchemy.text("TRUNCATE cart_ledgers"))

        # Get quantity and sku using cart_id in carts_and_items
        order_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM carts_and_items WHERE id = " + str(cart_id))).scalar_one()

        # Return purhcase info
        return {"total_potions_bought": order_quantity, "total_gold_paid": gold_sum}





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

        purple_sum = connection.execute(sqlalchemy.text("SELECT SUM(purple_change) FROM cart_ledgers")).scalar_one()
        purple_cur = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_stock where id = 6")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = :new_purple WHERE id = 6"), [{"new_purple": purple_sum + purple_cur}])

        gold_sum = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM cart_ledgers")).scalar_one()
        connection.execute(sqlalchemy.text("UPDATE resources SET gold = :goldsum + resources.gold"), [{"goldsum": gold_sum}])

        connection.execute(sqlalchemy.text("TRUNCATE cart_ledgers"))


        # Get quantity and sku using cart_id in carts_and_items
        order_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM carts_and_items WHERE id = " + str(cart_id))).scalar_one()

        # Return purhcase info
        return {"total_potions_bought": order_quantity, "total_gold_paid": gold_sum}