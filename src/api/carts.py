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

    order_by = sqlalchemy.desc(db.search_view.c.time)
    if sort_col is search_sort_options.customer_name:
        order_by = db.search_view.c.name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.search_view.c.sku
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.search_view.c.quantity
    elif sort_col is search_sort_options.timestamp:
        order_by = db.search_view.c.time
    else:
        assert False

    if(sort_order is search_sort_order.asc):
        order_by = sqlalchemy.asc(order_by)
    elif(sort_order is search_sort_order.desc):
        order_by = sqlalchemy.desc(order_by)

    with db.engine.begin() as connection:
        num_items = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM search_view")).scalar_one()
    num_pages = num_items/5
    if num_items % 5 != 0:
        num_pages += 1

    page = 0
    if search_page != "":
        # +1 because search_page is the index, not the actual page number
        page = int(search_page) + 1
    offset = 5 * page


    # offset = -1 is page 0, offset is the index of the pages
    # probably use the search_view thing instead of carts_and_customers
    if int(search_page) == 0:
        prev = ""
    else: 
        prev = int(search_page) - 1


    stmt = (
        sqlalchemy.select(
            db.search_view.c.id,
            db.search_view.c.sku,
            db.search_view.c.name,
            db.search_view.c.quantity,
            db.search_view.c.time,
        )
        .limit(6)
        .offset(offset)
        .order_by(order_by, db.search_view.c.id)
    )

    # filter only if parameter is passed
    if customer_name != "":
        stmt = stmt.where(db.search_view.c.name.ilike(f"%{customer_name}%"))
    if potion_sku != "":
        stmt = stmt.where(db.search_view.c.sku.ilike(f"%{potion_sku}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "previous": prev,
                    "next": "",
                    "results": [ 
                        {
                        "line_item_id": row.id,
                        "item_sku": row.sku,
                        "customer_name": row.name,
                        "line_item_total": row.quantity,
                        "timestamp": row.time,
                        }
                    ],
                }
            )

        if len(json) > 5:
            # it's just page b.c. page already has a +1 
            next = page
            json = []
            for row in result:
                json.append(
                    {
                        "previous": prev,
                        "next": next,
                        "results": [ 
                            {
                            "line_item_id": row.id,
                            "item_sku": row.sku,
                            "customer_name": row.name,
                            "line_item_total": row.quantity,
                            "timestamp": row.time,
                            }
                        ],
                    }
                )


    return json
    

    # make search_view in in SQLeditor
    # wanna use search_view to look at data... limit it... show specific qualities



    with db.engine.begin() as connection:

        connection.execute(sqlalchemy.text())














        customer_names = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY :col :ord"), [{"col": sort_col, "ord": sort_order}])
        quantities = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY :col :ord"), [{"col": sort_col, "ord": sort_order}])
        item_names = connection.execute(sqlalchemy.text("SELECT name FROM carts_and_customers GROUP BY :col :ord"), [{"col": sort_col, "ord": sort_order}])


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
        potion_price, potion_name = connection.execute(sqlalchemy.text("SELECT price, name FROM potion_stock WHERE sku = :ordersku"), [{"ordersku": item_sku}]).first()
        price = int(potion_price) * cart_item.quantity

        # Insert a potion new ledger
        connection.execute(sqlalchemy.text("INSERT INTO cart_ledgers (cart_id, gold_change, red_change) VALUES (:id, :price, :amount)"), [{"id": cart_id, "price": price, "amount": -cart_item.quantity, "color": potion_name[:-7] + "_change"}])


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        
        # Get all sums of cart ledgers
        red, green, blue, brown, purple, dark_red, dark_green, dark_blue, dark_brown, dark_purple, dark, white, gold_sum = connection.execute(sqlalchemy.text("""SELECT SUM(red_change), SUM(green_change), SUM(blue_change), 
                                                                                                                                                    SUM(brown_change), SUM(purple_change), SUM(dark_red_change), 
                                                                                                                                                    SUM(dark_green_change), SUM(dark_blue_change), SUM(dark_brown_change), 
                                                                                                                                                    SUM(dark_purple_change), SUM(dark_change), SUM(white_change), SUM(gold_change) FROM cart_ledgers""")).first()


        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :red_sum WHERE id = 1"), [{"red_sum": int(red),}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :green_sum WHERE id = 2"), [{"green_sum": int(green)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :blue_sum WHERE id = 3"), [{"blue_sum": int(blue)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :brown_sum WHERE id = 4"), [{"brown_sum": int(brown)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :purple_sum WHERE id = 6"), [{"purple_sum": int(purple)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_red_sum WHERE id = 7"), [{"dark_red_sum": int(dark_red)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_green_sum WHERE id = 8"), [{"dark_green_sum": int(dark_green)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_blue_sum WHERE id = 9"), [{"dark_blue_sum": int(dark_blue)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_brown_sum WHERE id = 10"), [{"dark_brown_sum": int(dark_brown)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_purple_sum WHERE id = 12"), [{"dark_purple_sum": int(dark_purple)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :dark_sum WHERE id = 13"), [{"dark_sum": int(dark)}])
        connection.execute(sqlalchemy.text("UPDATE potion_stock SET quantity = potion_stock.quantity - :white_sum WHERE id = 14"), [{"white_sum": int(white)}])
        connection.execute(sqlalchemy.text("UPDATE resources SET gold = :goldsum + resources.gold"), [{"goldsum": gold_sum}])

        
        # Clear all cart ledgers
        connection.execute(sqlalchemy.text("TRUNCATE cart_ledgers"))

        # Get quantity and sku using cart_id in carts_and_items
        order_quantity = connection.execute(sqlalchemy.text("SELECT quantity FROM carts_and_items WHERE id = " + str(cart_id))).scalar_one()

        # Return purhcase info
        return {"total_potions_bought": order_quantity, "total_gold_paid": gold_sum}