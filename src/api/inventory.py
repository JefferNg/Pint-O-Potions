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
        inventory = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold FROM global_inventory"))
        potions = connection.execute(sqlalchemy.text("SELECT quantity, sku FROM potion_inventory"))
        ledger = connection.execute(sqlalchemy.text
        ("SELECT SUM(gold_change) AS balance, SUM(red_ml_change) AS red_ml_change, SUM(green_ml_change) AS green_ml_change, SUM(blue_ml_change) AS blue_ml_change, SUM(dark_ml_change) AS dark_ml_change, SUM(red_potion_change) AS red_potion_change, SUM(green_potion_change) AS green_potion_change, SUM(blue_potion_change) AS blue_potion_change, SUM(dark_potion_change) AS dark_potion_change, SUM(purple_potion_change) AS purple_potion_change, SUM(forest_potion_change) AS forest_potion_change, SUM(navy_potion_change) AS navy_potion_change, SUM(maroon_potion_change) AS maroon_potion_change, SUM(unmarked_potion_change) AS unmarked_potion_change FROM shop_ledger WHERE customer_name = 'Shop'"))
        ledge_dict = {}
        for item in ledger:
            if item.balance is not None:
                print(f"gold: {item.balance}")
                print(f"red_ml: {item.red_ml_change}")
                print(f"green_ml: {item.green_ml_change}")
                print(f"blue_ml: {item.blue_ml_change}")
                print(f"dark_ml: {item.dark_ml_change}")
                print(f"red_potion: {item.red_potion_change}")
                print(f"green_potion: {item.green_potion_change}")
                print(f"blue_potion: {item.blue_potion_change}")
                print(f"dark_potion: {item.dark_potion_change}")
                print(f"purple_potion: {item.purple_potion_change}")
                print(f"forest_potion: {item.forest_potion_change}")
                print(f"navy_potion: {item.navy_potion_change}")
                print(f"maroon_potion: {item.maroon_potion_change}")
                print(f"unmarked_potion: {item.unmarked_potion_change}")
                ledge_dict["RED_POTION"] = item.red_potion_change
                ledge_dict["GREEN_POTION"] = item.green_potion_change
                ledge_dict["BLUE_POTION"] = item.blue_potion_change
                ledge_dict["DARK_POTION"] = item.dark_potion_change
                ledge_dict["PURPLE_POTION"] = item.purple_potion_change
                ledge_dict["FOREST_POTION"] = item.forest_potion_change
                ledge_dict["NAVY_POTION"] = item.navy_potion_change
                ledge_dict["MAROON_POTION"] = item.maroon_potion_change
                ledge_dict["UNMARKED_POTION"] = item.unmarked_potion_change
                ledge_dict["RED_ML"] = item.red_ml_change
                ledge_dict["GREEN_ML"] = item.green_ml_change
                ledge_dict["BLUE_ML"] = item.blue_ml_change
                ledge_dict["DARK_ML"] = item.dark_ml_change
                ledge_dict["GOLD"] = item.balance
        

        num = 0
        ml = 0
        gold = 0
        for row in potions:
            if len(ledge_dict) > 0:
                connection.execute(sqlalchemy.text
                ("UPDATE potion_inventory SET quantity = :quantity WHERE sku = :sku"),
                [{"quantity": ledge_dict[row.sku], "sku": row.sku}])
            num += ledge_dict[row.sku]
        for row in inventory:
            if len(ledge_dict) > 0:
                connection.execute(sqlalchemy.text
                ("UPDATE global_inventory SET num_red_ml = :red, num_green_ml = :green, num_blue_ml = :blue, num_dark_ml = :dark, gold = :gold"),
                [{"red": ledge_dict["RED_ML"], "green": ledge_dict["GREEN_ML"], "blue": ledge_dict["BLUE_ML"], "dark": ledge_dict["DARK_ML"], "gold": ledge_dict["GOLD"]}])
            ml = ledge_dict["RED_ML"] + ledge_dict["GREEN_ML"] + ledge_dict["BLUE_ML"] + ledge_dict["DARK_ML"]
            gold = ledge_dict["GOLD"]
        #connection.execute(sqlalchemy.text("TRUNCATE shop_ledger CASCADE"))
        # connection.execute(sqlalchemy.text
        # ("INSERT INTO shop_ledger (gold_change, red_ml_change, green_ml_change, blue_ml_change, dark_ml_change, red_potion_change, green_potion_change, blue_potion_change, dark_potion_change, purple_potion_change, forest_potion_change, navy_potion_change, maroon_potion_change, unmarked_potion_change, customer_name) VALUES (:gold, :red_ml, :green_ml, :blue_ml, :dark_ml, :red_potion, :green_potion, :blue_potion, :dark_potion, :purple_potion, :forest_potion, :navy_potion, :maroon_potion, :unmarked_potion, 'Shop')"),
        # [{"gold": ledge_dict["GOLD"], "red_ml": ledge_dict["RED_ML"], "green_ml": ledge_dict["GREEN_ML"], "blue_ml": ledge_dict["BLUE_ML"], "dark_ml": ledge_dict["DARK_ML"], "red_potion": ledge_dict["RED_POTION"], "green_potion": ledge_dict["GREEN_POTION"], "blue_potion": ledge_dict["BLUE_POTION"], "dark_potion": ledge_dict["DARK_POTION"], "purple_potion": ledge_dict["PURPLE_POTION"], "forest_potion": ledge_dict["FOREST_POTION"], "navy_potion": ledge_dict["NAVY_POTION"], "maroon_potion": ledge_dict["MAROON_POTION"], "unmarked_potion": ledge_dict["UNMARKED_POTION"]}])
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
        result = connection.execute(sqlalchemy.text("SELECT potion_capacity, ml_capacity, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory"))
        potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory"))
        total_potions = 0
        for potion in potions:
            total_potions += potion.quantity
        for row in result:
            capacity["potion_capacity"] = row.potion_capacity - total_potions
            capacity["ml_capacity"] = row.ml_capacity - (row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml)

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
        result = connection.execute(sqlalchemy.text("SELECT potion_capacity, ml_capacity, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold FROM global_inventory"))
        potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory"))
        total_potions = 0
        total_ml = 0
        for potion in potions:
            total_potions += potion.quantity
        for row in result:
            total_ml = row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml
            if total_potions > 50 or total_ml > 10000:
                if row.gold - 1000 > 0:
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET potion_capacity = :pot_cap, ml_capacity = :ml_cap"),
                    [{"pot_cap": row.potion_capacity + capacity_purchase.potion_capacity, "ml_cap": row.ml_capacity + capacity_purchase.ml_capacity}])
                    transaction = connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_transactions (description) VALUES ('Shop paid 1000 to increase inventory capacity') RETURNING id"))
                    tid = 0
                    for t in transaction:
                        tid = t.id
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (gold_change, customer_name, transaction_id) VALUES (-1000, 'Shop', :tid)"),
                    [{"tid": tid}])


    return "OK"
