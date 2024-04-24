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
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory"))
        num = 0
        ml = 0
        gold = 0
        for row in potions:
            num += row.quantity
        for row in inventory:
            ml = row.num_green_ml + row.num_red_ml + row.num_blue_ml + row.num_dark_ml
            gold = row.gold
    return {"number_of_potions": num, "ml_in_barrels": ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    capacity = {}
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            capacity["potion_capacity"] = row.potion_capacity
            capacity["ml_capacity"] = row.ml_capacity

    return capacity

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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        total_potions = 0
        total_ml = 0
        for row in result:
            total_potions = row.num_red_potions + row.num_green_potions + row.num_blue_potions + row.num_dark_potions
            total_ml = row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml
            if total_potions > 50 or total_ml > 10000:
                if row.gold - 1000 > 0:
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET potion_capacity = :pot_cap, ml_capacity = :ml_cap, gold = :gold"),
                    [{"pot_cap": row.potion_capacity + capacity_purchase.potion_capacity, "ml_cap": row.ml_capacity + capacity_purchase.ml_capacity, "gold": row.gold - 1000}])


    return "OK"
