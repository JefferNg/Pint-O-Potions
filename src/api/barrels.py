from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            if barrel.potion_type == [0,1,0,0]:
                tid = connection.execute(sqlalchemy.text
                ("INSERT INTO shop_transactions (description) VALUES ('Shop paid Roxanne :paid for green barrel') RETURNING id"),
                [{"paid": barrel.price * barrel.quantity}]).scalar_one()
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, green_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Shop', :tid)"),
                [{"val": -barrel.price * barrel.quantity, "ml": barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, green_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Roxanne', :tid)"),
                [{"val": barrel.price * barrel.quantity, "ml": -barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
            elif barrel.potion_type == [1,0,0,0]:
                tid = connection.execute(sqlalchemy.text
                ("INSERT INTO shop_transactions (description) VALUES ('Shop paid Roxanne :paid for red barrel') RETURNING id"),
                [{"paid": barrel.price * barrel.quantity}]).scalar_one()
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, red_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Shop', :tid)"),
                [{"val": -barrel.price * barrel.quantity, "ml": barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, red_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Roxanne', :tid)"),
                [{"val": barrel.price * barrel.quantity, "ml": -barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
            elif barrel.potion_type == [0,0,1,0]:
                tid = connection.execute(sqlalchemy.text
                ("INSERT INTO shop_transactions (description) VALUES ('Shop paid Roxanne :paid for blue barrel') RETURNING id"),
                [{"paid": barrel.price * barrel.quantity}]).scalar_one()
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, blue_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Shop', :tid)"),
                [{"val": -barrel.price * barrel.quantity, "ml": barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, blue_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Roxanne', :tid)"),
                [{"val": barrel.price * barrel.quantity, "ml": -barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
            elif barrel.potion_type == [0,0,0,1]:
                tid = connection.execute(sqlalchemy.text
                ("INSERT INTO shop_transactions (description) VALUES ('Shop paid Roxanne :paid for dark barrel') RETURNING id"),
                [{"paid": barrel.price * barrel.quantity}]).scalar_one()
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, dark_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Shop', :tid)"),
                [{"val": -barrel.price * barrel.quantity, "ml": barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
                connection.execute(sqlalchemy.text
                ("INSERT INTO shop_ledger (gold_change, dark_ml_change, customer_name, transaction_id) VALUES (:val, :ml, 'Roxanne', :tid)"),
                [{"val": barrel.price * barrel.quantity, "ml": -barrel.ml_per_barrel * barrel.quantity, "tid": tid}])
            print(barrel.sku)


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    MAX = 10
    LIMITER = 2
    with db.engine.begin() as connection:
        capacity = connection.execute(sqlalchemy.text("SELECT ml_capacity FROM global_inventory")).scalar_one()
        ledger = connection.execute(sqlalchemy.text
        ("SELECT SUM(gold_change) AS gold, SUM(red_ml_change) AS red_ml_change, SUM(green_ml_change) AS green_ml_change, SUM(blue_ml_change) AS blue_ml_change, SUM(dark_ml_change) AS dark_ml_change FROM shop_ledger WHERE customer_name = 'Shop'"))
        gold = 0
        ml_inventory = {}
        num_red_ml = 0
        num_green_ml = 0
        num_blue_ml = 0
        num_dark_ml = 0
        total_ml = 0
        for row in ledger:
            gold = row.gold
            ml_inventory["red_ml"] = row.red_ml_change
            ml_inventory["green_ml"] = row.green_ml_change
            ml_inventory["blue_ml"] = row.blue_ml_change
            ml_inventory["dark_ml"] = row.dark_ml_change
            total_ml = row.red_ml_change + row.green_ml_change + row.blue_ml_change + row.dark_ml_change

    barrel_plan = []
    for barrel in wholesale_catalog:
        # cycle through different barrels
        num_possible_purchase = gold//barrel.price
        for ml in ml_inventory:
            if num_possible_purchase > 0 and ml_inventory.get(ml) < 1000:
                # buy barrel based on demand
                if num_possible_purchase <= barrel.quantity:
                    # should buy max 10 barrels of each type
                    if num_possible_purchase < MAX and num_possible_purchase * barrel.ml_per_barrel + total_ml <= capacity:
                        # number of barrels purchased should not exceed ml capacity
                        barrel_plan.append({
                            "sku": barrel.sku,
                            "ml_per_barrel": barrel.ml_per_barrel,
                            "potion_type": barrel.potion_type,
                            "price": barrel.price,
                            "quantity": num_possible_purchase
                        })
                        gold -= barrel.price * num_possible_purchase
                        total_ml += num_possible_purchase * barrel.ml_per_barrel
                    elif total_ml + MAX * barrel.ml_per_barrel <= capacity:
                        # max barrels purchased should not exceed ml capacity
                        barrel_plan.append({
                            "sku": barrel.sku,
                            "ml_per_barrel": barrel.ml_per_barrel,
                            "potion_type": barrel.potion_type,
                            "price": barrel.price,
                            "quantity": MAX
                        })
                        gold -= barrel.price * MAX
                        total_ml += MAX * barrel.ml_per_barrel
                    break
                elif "large" in barrel.sku.lower():
                    # buy based on sku
                    remaining_ml = capacity - total_ml
                    if total_ml + barrel.ml_per_barrel * barrel.quantity <= capacity:
                        barrel_plan.append({
                                "sku": barrel.sku,
                                "ml_per_barrel": barrel.ml_per_barrel,
                                "potion_type": barrel.potion_type,
                                "price": barrel.price,
                                "quantity": barrel.quantity // LIMITER
                            })
                        gold -= barrel.price * barrel.quantity // LIMITER
                        total_ml += barrel.quantity // LIMITER * barrel.ml_per_barrel
                    elif remaining_ml // barrel.ml_per_barrel > 0:
                        barrel_plan.append({
                                "sku": barrel.sku,
                                "ml_per_barrel": barrel.ml_per_barrel,
                                "potion_type": barrel.potion_type,
                                "price": barrel.price,
                                "quantity": remaining_ml // barrel.ml_per_barrel
                            })
                        gold -= barrel.price * remaining_ml // barrel.ml_per_barrel
                        total_ml += remaining_ml // barrel.ml_per_barrel * barrel.ml_per_barrel
                    break

    print(f"Current barrel plan: {barrel_plan}")

    return barrel_plan


