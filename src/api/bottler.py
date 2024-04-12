from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            if row.num_green_ml / (100 * potions_delivered[0].quantity) > 0:
                result = connection.execute(sqlalchemy.text
                (f"UPDATE global_inventory SET num_green_potions = {
                    potions_delivered[0].quantity + row.num_green_potions}"))
                result = connection.execute(sqlalchemy.text
                (f"UPDATE global_inventory SET num_green_ml = {
                    row.num_green_ml - (100 * potions_delivered[0].quantity)}"))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    ml = 0
    for row in result:
        ml = row.num_green_ml
    num = ml % 100
    ml /= 100
    if ml > 0:
        num += 1
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())