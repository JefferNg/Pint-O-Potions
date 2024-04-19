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
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_green_ml = {(barrel.ml_per_barrel + row.num_green_ml)*barrel.quantity}"))
                if barrel.potion_type == [1,0,0,0]:
                    if row.num_red_potions < 15:
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_red_ml = {(barrel.ml_per_barrel + row.num_red_ml)*barrel.quantity}"))
                if barrel.potion_type == [0,0,1,0]:
                    if row.num_blue_potions < 5:
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_blue_ml = {(barrel.ml_per_barrel + row.num_blue_ml)*barrel.quantity}"))
                if barrel.potion_type == [0,0,0,1]:
                    if row.num_dark_potions < 5:
                        result = connection.execute(sqlalchemy.text
                        (f"UPDATE global_inventory SET num_dark_ml = {(barrel.ml_per_barrel + row.num_dark_ml)*barrel.quantity}"))


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
        if (barrel.potion_type == [1,0,0,0]):
            if barrel.price <= gold:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": 1,
                })
        elif (barrel.potion_type == [0,1,0,0]):
            if barrel.price <= gold:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": 1,
                })
        elif (barrel.potion_type == [0,0,1,0]):
            if barrel.price <= gold:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": 1,
                })
        elif (barrel.potion_type == [0,0,0,1]):
            if barrel.price <= gold:
                barrel_plan.append(        {
                    "sku": barrel.sku,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type,
                    "price": barrel.price,
                    "quantity": 1,
                })
        else:
            raise Exception("Invalid Potion Type")


    return barrel_plan


