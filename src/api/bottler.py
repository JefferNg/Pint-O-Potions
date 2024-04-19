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
        potion_mix = potions_delivered[0].potion_type
        for row in result:
            for potions in potions_delivered:
                if potion_mix[0] == 100:
                    # update red bottle and ml count
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_red_potions = {potions.quantity + row.num_red_potions}"))
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_red_ml = {row.num_red_ml - potion_mix[0]}"))
                elif potion_mix[1] == 100:
                    # update green bottle and ml count
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_green_potions = {potions.quantity + row.num_green_potions}"))
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_green_ml = {row.num_green_ml - potion_mix[1]}"))
                elif potion_mix[2] == 100:
                    # update blue bottle and ml count
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_blue_potions = {potions.quantity + row.num_blue_potions}"))
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_blue_ml = {row.num_blue_ml - potion_mix[2]}"))
                elif potion_mix[3] == 100:
                    # update dark bottle and ml count
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_dark_potions = {potions.quantity + row.num_dark_potions}"))
                    result = connection.execute(sqlalchemy.text
                    (f"UPDATE global_inventory SET num_dark_ml = {row.num_dark_ml - potion_mix[3]}"))
                else:
                    raise Exception("No Potion Mixed")

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
        green_ml = 0
        red_ml = 0
        blue_ml = 0
        dark_ml = 0
        for row in result:
            green_ml = row.num_green_ml
            red_ml = row.num_red_ml
            blue_ml = row.num_blue_ml
            dark_ml = row.num_dark_ml

    bottle_plan = []

    # red_mix = 0
    # blue_mix = 0

    if green_ml >= 100:
        # bottle only green
        bottle_plan.append({
            "potion_type": [100, 0, 0, 0],
            "quantity": 1,
        })
    elif red_ml >= 100:
        # bottle only red
        bottle_plan.append({
            "potion_type": [0, 100, 0, 0],
            "quantity": 1,
        })
    elif blue_ml >= 100:
        # bottle only blue
        bottle_plan.append({
            "potion_type": [0, 0, 100, 0],
            "quantity": 1,
        })
    elif dark_ml >= 100:
        # bottle only dark
        bottle_plan.append({
            "potion_type": [0, 0, 0, 100],
            "quantity": 1,
        })
    else:
        # bottle no potions
        bottle_plan.append({
             "potion_type": [0, 0, 0, 0],
             "quantity": 0,
         })
    

    ### VERSION 3 (did too much, whoops):

    # elif green_ml + red_ml + blue_ml < 100:
    #     # do not bottle because not enough supplies
    #     bottle_plan.append({
    #         "potion_type": [0, 0, 0, 0],
    #         "quantity": 0,
    #     })
    # else:
    #     # mix green first, then red, then blue
    #     total = green_ml
    #     for i in range(1, red_ml):
    #         if total + i > 100:
    #             break
    #         total += 1
    #         red_mix += 1
    #     for i in range(1, blue_ml):
    #         if total + 1 > 100:
    #             break
    #         total += 1
    #         blue_mix += 1
        
    #     bottle_plan.append({
    #         "potion_type": [green_ml, red_mix, blue_mix, 0],
    #         "quantity": 1,
    #     })



    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())