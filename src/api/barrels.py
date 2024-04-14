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
        if row.num_green_potions < 10:
            for barrel in barrels_delivered:
                if barrel.sku == "SMALL_GREEN_BARREL":
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_green_ml = {(barrels_delivered[0].ml_per_barrel + row.num_green_ml)*barrels_delivered[0].quantity}"))

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

    num = 0
    barrel_plan = []
    for barrel in wholesale_catalog:
        # cycle through different barrels
        if (barrel.sku == "SMALL_GREEN_BARREL"):
            if wholesale_catalog[0].price <= gold:
                barrel_plan.append(        {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1
                })


    return barrel_plan


