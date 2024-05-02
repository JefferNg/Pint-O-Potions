from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
import random

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
                "item_sku": potion_sku,
                "customer_name": customer_name,
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
    print(f"A customer visited the shop! \n{customers}")
    
    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    print(f"Cart created by: {new_cart}")

    with db.engine.begin() as connection:
        # customer = connection.execute(sqlalchemy.text
        # ("INSERT INTO customers (name, class, level) VALUES (:name, :class, :level) RETURNING id"), 
        # [{"name": new_cart.customer_name, "class": new_cart.character_class, "level": new_cart.level}])
        # cust_id = 0
        # for cust in customer:
        #     connection.execute(sqlalchemy.text
        #     ("INSERT INTO carts (customer) VALUES (:customer)"), 
        #     [{"customer": cust.id}])
        #     cust_id = cust.id
        connection.execute(sqlalchemy.text
        ("INSERT INTO carts (customer) VALUES (:customer)"), 
        [{"customer": new_cart.customer_name}])
        result = connection.execute(sqlalchemy.text("SELECT id, customer FROM carts"))
        cart_num = 0
        for row in result:
            if new_cart.customer_name in row.customer:
                cart_num = row.id

    return {"cart_id": cart_num}


class CartItem(BaseModel):
    quantity: int

# convert sku to id
sku_values = {
    "RED_POTION": 1,
    "GREEN_POTION": 2,
    "BLUE_POTION" : 3,
    "DARK_POTION": 4,
    "PURPLE_POTION": 5,
    "FOREST_POTION": 6,
    "NAVY_POTION": 7,
    "MAROON_POTION": 8,
    "UNMARKED_POTION": 9
}

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print(f"A customer wants to buy {cart_item.quantity, item_sku}")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT sku, quantity FROM potion_inventory"))
        carts = connection.execute(sqlalchemy.text("SELECT id FROM carts"))
        
        for cart in carts:
            if cart.id == cart_id:
                for row in result:
                    if item_sku == row.sku:
                        total = connection.execute(sqlalchemy.text(f"SELECT SUM({row.sku.lower() + '_change'}) FROM shop_ledger WHERE customer_name = 'Shop'")).scalar_one()
                        if total - cart_item.quantity >= 0:
                            # add potion to cart
                            connection.execute(sqlalchemy.text
                            ("INSERT INTO cart_items (cart_id, item_sku, quantity) VALUES (:cart_id, :item_sku, :quantity)"), 
                            [{"cart_id": cart_id, "item_sku": sku_values.get(item_sku), "quantity": cart_item.quantity}])
                            print(f"item {item_sku, cart_item} added to cart id {cart_id}")
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print(f"payment: {cart_checkout.payment}")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT id, sku, quantity, price FROM potion_inventory"))
        carts = connection.execute(sqlalchemy.text("SELECT id, customer FROM carts"))
        # inventory = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        total = 0
        # gold = 0
        paid = 0
        # for g in inventory:
        #     gold = g.gold
        for cart in carts:
            if cart.id == cart_id:
                items = connection.execute(sqlalchemy.text
                ("SELECT item_sku, quantity FROM cart_items WHERE cart_id = :id"), [{"id": cart_id}])
                list_of_items = {}
                for item in items:
                    # add items in cart to local dictionary
                    if item.item_sku in list_of_items:
                        # update quantity if item in dictionary
                        list_of_items.update({item.item_sku: list_of_items.get(item.item_sku) + item.quantity})
                    else:
                        # add new item to dictionary
                        list_of_items[item.item_sku] = item.quantity
                    # delete item from cart_item table once processed
                    connection.execute(sqlalchemy.text
                    ("DELETE FROM cart_items WHERE item_sku = :sku"), [{"sku": item.item_sku}])
                
                for row in result:
                    if row.id in list_of_items:
                        # potion item in cart
                        total += list_of_items.get(row.id)
                        # connection.execute(sqlalchemy.text
                        # ("UPDATE potion_inventory SET quantity = :total WHERE sku = :sku"), 
                        # [{"total": row.quantity - list_of_items.get(row.id), "sku": row.sku}])
                        
                        paid += row.price * list_of_items.get(row.id)
                    for item in list_of_items:
                        if sku_values.get(row.sku) == item:
                            tid = connection.execute(sqlalchemy.text
                            ("INSERT INTO shop_transactions (description) VALUES (:text) RETURNING id"), 
                            [{"text": f"{cart.customer} paid {row.price * list_of_items.get(row.id)} gold for {list_of_items.get(row.id)} {row.sku.lower()}"}]).scalar_one()
                            connection.execute(sqlalchemy.text
                            (f"INSERT INTO shop_ledger ({row.sku.lower()}_change, gold_change, customer_name, transaction_id) VALUES (:quantity, :paid, :name, :tid)"),
                            [{"quantity": list_of_items.get(row.id), "paid": -row.price * list_of_items.get(row.id), "name": cart.customer, "tid": tid}])
                            connection.execute(sqlalchemy.text
                            (f"INSERT INTO shop_ledger ({row.sku.lower()}_change, gold_change, customer_name, transaction_id) VALUES (:quantity, :paid, :name, :tid)"),
                            [{"quantity": -list_of_items.get(row.id), "paid": row.price * list_of_items.get(row.id), "name": "Shop", "tid": tid}])
        # connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :gold"), [{"gold": gold + paid}])
        connection.execute(sqlalchemy.text("DELETE FROM carts WHERE id = :id"), [{"id": cart_id}])
    return {"total_potions_bought": total, "total_gold_paid": paid}
