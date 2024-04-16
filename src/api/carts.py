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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
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
    print(customers)
    
    return "OK"

class Cart:
    def __init__(self, cart_id, customer, potion_quantity):
        self.cart_id = cart_id
        self.customer = customer
        self.potion_quantity = potion_quantity

cart_dict = {
    "cart": []
}


cart_num = 0

@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    global cart_num
    cart_num += 1
    cart = Cart(cart_num, new_cart, {})
    cart_list = cart_dict.get("cart")
    cart_list.append(cart)
    cart_dict.update({"cart": cart_list})
    return {"cart_id": cart_num}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    for row in result:
        for cart in cart_dict.get("cart"):
            if cart.cart_id == cart_id:
                if item_sku == "GREEN_POTIONS_0":
                    if row.num_green_potions - cart_item.quantity > 0:
                        cart.potion_quantity.update({item_sku: cart_item.quantity})
                if item_sku == "RED_POTIONS_0":
                    if row.num_red_potions - cart_item.quantity > 0:
                        cart.potion_quantity.update({item_sku: cart_item.quantity})
                if item_sku == "BLUE_POTIONS_0":
                    if row.num_blue_potions - cart_item.quantity > 0:
                        cart.potion_quantity.update({item_sku: cart_item.quantity})  
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    total = 0
    for row in result:
        for cart in cart_dict.get("cart"):
            if cart.cart_id == cart_id:
                for potion in cart.potion_quantity.keys():
                    if potion == "GREEN_POTIONS_0":
                        total += cart.potion_quantity.get(potion)
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_green_potions = {row.num_green_potions - cart.quantity}"))
                        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {row.gold + cart.quantity * 50}"))
                    if potion == "RED_POTIONS_0":
                        total += cart.potion_quantity.get(potion)
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_red_potions = {row.num_red_potions - cart.quantity}"))
                        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {row.gold + cart.quantity * 50}"))
                    if potion == "BLUE_POTIONS_0":
                        total += cart.potion_quantity.get(potion)
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_blue_potions = {row.num_blue_potions - cart.quantity}"))
                        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {row.gold + cart.quantity * 50}"))
    return {"total_potions_bought": total, "total_gold_paid": total * 50}
