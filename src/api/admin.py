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
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100, num_red_ml = 0, num_green_ml = 0, num_blue_ml = 0, num_dark_ml = 0, potion_capacity = 50, ml_capacity = 10000"))
        connection.execute(sqlalchemy.text("UPDATE potion_inventory SET quantity = 0"))
        connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE cart_items CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE shop_ledger CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE shop_transactions CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE potion_history CASCADE"))
        connection.execute(sqlalchemy.text("INSERT INTO shop_ledger (gold_change, customer_name) VALUES (100, 'Shop')"))

    return "OK"

