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
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            for barrel in barrels_delivered:
                if barrel.potion_type == [0,1,0,0]:
                    if row.num_green_potions < 10:
                        connection.execute(sqlalchemy.text
                        ("UPDATE global_inventory SET num_green_ml = :ml"), 
                        [{"ml": row.num_green_ml + (barrel.ml_per_barrel*barrel.quantity)}])
                        # connection.execute(sqlalchemy.text
                        # ("INSERT INTO shop_transactions (description) VALUES ('Shop paid Roxanne :paid for :purchase')"),
                        # [{"paid": row.gold - barrel.price * barrel.quantity, "purchase": barrel.sku}])
                elif barrel.potion_type == [1,0,0,0]:
                    if row.num_red_potions < 15:
                        connection.execute(sqlalchemy.text
                        ("UPDATE global_inventory SET num_red_ml = :ml"), 
                        [{"ml": row.num_red_ml + (barrel.ml_per_barrel*barrel.quantity)}])
                elif barrel.potion_type == [0,0,1,0]:
                    if row.num_blue_potions < 5:
                        connection.execute(sqlalchemy.text
                        ("UPDATE global_inventory SET num_blue_ml = :ml"), 
                        [{"ml": row.num_blue_ml + (barrel.ml_per_barrel*barrel.quantity)}])
                elif barrel.potion_type == [0,0,0,1]:
                    if row.num_dark_potions < 5:
                        connection.execute(sqlalchemy.text
                        ("UPDATE global_inventory SET num_dark_ml = :ml"), 
                        [{"ml": row.num_dark_ml + (barrel.ml_per_barrel*barrel.quantity)}])
                connection.execute(sqlalchemy.text
                        ("UPDATE global_inventory SET gold = :gold"),
                        [{"gold": row.gold - barrel.price * barrel.quantity}])


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        gold = 0
        for row in result:
            gold = row.gold

    barrel_plan = []
    for barrel in wholesale_catalog:
        # cycle through different barrels
        num_possible_purchase = int(gold/barrel.price)
        if (barrel.potion_type == [1,0,0,0]):
            if num_possible_purchase > 0:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": num_possible_purchase,
                })
                #gold -= barrel.price * num_possible_purchase
        elif (barrel.potion_type == [0,1,0,0]):
            if num_possible_purchase > 0:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": num_possible_purchase,
                })
                #gold -= barrel.price * num_possible_purchase
        elif (barrel.potion_type == [0,0,1,0]):
            if num_possible_purchase > 0:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": num_possible_purchase,
                })
                #gold -= barrel.price * num_possible_purchase
        elif (barrel.potion_type == [0,0,0,1]):
            if num_possible_purchase > 0:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": num_possible_purchase,
                })
                #gold -= barrel.price * num_possible_purchase
        # else:
        #     raise Exception("Invalid Potion Type")


    return barrel_plan


