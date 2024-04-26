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
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        potion_inventory = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        red_potions = 0
        green_potions = 0
        blue_potions = 0
        dark_potions = 0
        purple_potions = 0
        forest_potions = 0
        navy_potions = 0
        maroon_potions = 0
        unmarked_potions = 0
        for potion in potion_inventory:
            if potion.sku == "RED_POTION":
                red_potions = potion.quantity
            elif potion.sku == "GREEN_POTION":
                green_potions = potion.quantity
            elif potion.sku == "BLUE_POTION":
                blue_potions = potion.quantity
            elif potion.sku == "DARK_POTION":
                dark_potions = potion.quantity
            elif potion.sku == "PURPLE_POTION":
                purple_potions = potion.quantity
            elif potion.sku == "FOREST_POTION":
                forest_potions = potion.quantity
            elif potion.sku == "NAVY_POTION":
                navy_potions = potion.quantity
            elif potion.sku == "MAROON_POTION":
                maroon_potions = potion.quantity
            elif potion.sku == "UNMARKED_POTION":
                unmarked_potions = potion.quantity
        
        for row in inventory:
            red_ml = row.num_red_ml
            green_ml = row.num_green_ml
            blue_ml = row.num_blue_ml
            dark_ml = row.num_dark_ml
            for potions in potions_delivered:
                if potions.potion_type == [100,0,0,0]:
                    # update red bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + red_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_red_ml = :ml"),
                    [{"ml": red_ml - potions.potion_type[0]}])
                elif potions.potion_type == [0,100,0,0]:
                    # update green bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + green_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_green_ml = :ml"),
                    [{"ml": green_ml - potions.potion_type[1]}])
                elif potions.potion_type == [0,0,100,0]:
                    # update blue bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + blue_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_blue_ml = :ml"),
                    [{"ml": blue_ml - potions.potion_type[2]}])
                elif potions.potion_type == [0,0,0,100]:
                    # update dark bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + dark_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_dark_ml = :ml"),
                    [{"ml": dark_ml - potions.potion_type[3]}])
                elif potions.potion_type == [50,0,50,0]:
                    # update purple bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + purple_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_red_ml = :red_ml, num_blue_ml = :blue_ml"),
                    [{"red_ml": red_ml - potions.potion_type[0], "blue_ml": blue_ml - potions.potion_type[2]}])
                elif potions.potion_type == [0,50,0,50]:
                    # update forest bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + forest_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_green_ml = :green_ml, num_dark_ml = :dark_ml"),
                    [{"green_ml": green_ml - potions.potion_type[1], "dark_ml": dark_ml - potions.potion_type[3]}])
                elif potions.potion_type == [0,0,50,50]:
                    # update navy bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + navy_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_blue_ml = :blue_ml, num_dark_ml = :dark_ml"),
                    [{"blue_ml": blue_ml - potions.potion_type[2], "dark_ml": dark_ml - potions.potion_type[3]}])
                elif potions.potion_type == [50,0,0,50]:
                    # update maroon bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + maroon_potions, "type": potions.potion_type}])
                    connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_red_ml = :red_ml, num_dark_ml = :dark_ml"),
                    [{"red_ml": red_ml - potions.potion_type[0], "dark_ml": dark_ml - potions.potion_type[3]}])
                elif potions.potion_type == [25,25,25,25]:
                    # update unmarked bottle and ml count
                    connection.execute(sqlalchemy.text
                    ("UPDATE potion_inventory SET quantity = :quantity WHERE type = :type"),
                    [{"quantity": potions.quantity + unmarked_potions, "type": potions.potion_type}])
                    result = connection.execute(sqlalchemy.text
                    ("UPDATE global_inventory SET num_red_ml = :red_ml, num_green_ml = :green_ml, num_blue_ml = :blue_ml, num_dark_ml = :dark_ml"),
                    [{"red_ml": red_ml - potions.potion_type[0], "green_ml": green_ml - potions.potion_type[1], "blue_ml": blue_ml - potions.potion_type[2], "dark_ml": dark_ml - potions.potion_type[3]}])
                else:
                    raise Exception("No Potion Mixed")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    print("Getting potion plan")
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

        # bottle no potions if ml not sufficient
        bottle_plan = []

        if red_ml >= 50 and blue_ml >= 50:
            # bottle purple
            bottle_plan.append({
                "potion_type": [50, 0, 50, 0],
                "quantity": 1,
            })

        if blue_ml >= 50 and dark_ml >= 50:
            # bottle navy
            bottle_plan.append({
                "potion_type": [0, 0, 50, 50],
                "quantity": 1,
            })
        
        if red_ml >= 50 and dark_ml >= 50:
            # bottle maroon
            bottle_plan.append({
                "potion_type": [50, 0, 0, 50],
                "quantity": 1,
            })

        if green_ml >= 50 and dark_ml >= 50:
            # bottle forest
            bottle_plan.append({
                "potion_type": [0, 50, 0, 50],
                "quantity": 1,
            })

        if red_ml >= 25 and green_ml >= 25 and blue_ml >= 25 and dark_ml >= 25:
            # bottle useless
            bottle_plan.append({
                "potion_type": [25, 25, 25, 25],
                "quantity": 1,
            })
        if green_ml >= 100:
            # bottle only green
            bottle_plan.append({
                "potion_type": [0, 100, 0, 0],
                "quantity": int(green_ml/100),
            })
        if red_ml >= 100:
            # bottle only red
            bottle_plan.append({
                "potion_type": [100, 0, 0, 0],
                "quantity": int(red_ml/100),
            })
        if blue_ml >= 100:
            # bottle only blue
            bottle_plan.append({
                "potion_type": [0, 0, 100, 0],
                "quantity": int(blue_ml/100),
            })
        if dark_ml >= 100:
            # bottle only dark
            bottle_plan.append({
                "potion_type": [0, 0, 0, 100],
                "quantity": int(dark_ml/100),
            })

    print(f"Current bottle plan: {bottle_plan}" )

    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())