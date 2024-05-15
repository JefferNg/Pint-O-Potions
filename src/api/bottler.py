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
        ledger = connection.execute(sqlalchemy.text
        ("SELECT SUM(red_ml_change) AS red_ml_change, SUM(green_ml_change) AS green_ml_change, SUM(blue_ml_change) AS blue_ml_change, SUM(dark_ml_change) AS dark_ml_change, SUM(red_potion_change) AS red_potion_change, SUM(green_potion_change) AS green_potion_change, SUM(blue_potion_change) AS blue_potion_change, SUM(dark_potion_change) AS dark_potion_change, SUM(purple_potion_change) AS purple_potion_change, SUM(forest_potion_change) AS forest_potion_change, SUM(navy_potion_change) AS navy_potion_change, SUM(maroon_potion_change) AS maroon_potion_change, SUM(unmarked_potion_change) AS unmarked_potion_change FROM shop_ledger WHERE customer_name = 'Shop'"))
        red_potions = 0
        green_potions = 0
        blue_potions = 0
        dark_potions = 0
        purple_potions = 0
        forest_potions = 0
        navy_potions = 0
        maroon_potions = 0
        unmarked_potions = 0
        for row in ledger:
            red_potions = row.red_potion_change
            green_potions = row.green_potion_change
            blue_potions = row.blue_potion_change
            dark_potions = row.dark_potion_change
            purple_potions = row.purple_potion_change
            forest_potions = row.forest_potion_change
            navy_potions = row.navy_potion_change
            maroon_potions = row.maroon_potion_change
            unmarked_potions = row.unmarked_potion_change
            red_ml = row.red_ml_change
            green_ml = row.green_ml_change
            blue_ml = row.blue_ml_change
            dark_ml = row.dark_ml_change
            for potions in potions_delivered:
                if potions.potion_type == [100,0,0,0]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (red_ml_change, red_potion_change, customer_name) VALUES (:ml, :potion, 'Shop')"),
                    [{"ml": -potions.potion_type[0] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [0,100,0,0]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (green_ml_change, green_potion_change, customer_name) VALUES (:ml, :potion, 'Shop')"),
                    [{"ml": -potions.potion_type[1] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [0,0,100,0]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (blue_ml_change, blue_potion_change, customer_name) VALUES (:ml, :potion, 'Shop')"),
                    [{"ml": -potions.potion_type[2] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [0,0,0,100]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (dark_ml_change, dark_potion_change, customer_name) VALUES (:ml, :potion. 'Shop')"),
                    [{"ml": -potions.potion_type[3] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [50,0,50,0]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (red_ml_change, blue_ml_change, purple_potion_change, customer_name) VALUES (:ml_red, :ml_blue, :potion, 'Shop')"),
                    [{"ml_red": -potions.potion_type[0] * potions.quantity, "ml_blue": -potions.potion_type[2] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [0,50,0,50]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (green_ml_change, dark_ml_change, forest_potion_change, customer_name) VALUES (:ml_green, :ml_dark, :potion, 'Shop')"),
                    [{"ml_green": -potions.potion_type[1] * potions.quantity, "ml_dark": -potions.potion_type[3] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [0,0,50,50]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (blue_ml_change, dark_ml_change, navy_potion_change, customer_name) VALUES (:ml_blue, :ml_dark, :potion, 'Shop')"),
                    [{"ml_blue": -potions.potion_type[2] * potions.quantity, "ml_dark": -potions.potion_type[3] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [50,0,0,50]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (red_ml_change, dark_ml_change, maroon_potion_change, customer_name) VALUES (:ml_red, :ml_dark, :potion, 'Shop')"),
                    [{"ml_red": -potions.potion_type[0] * potions.quantity, "ml_dark": -potions.potion_type[3] * potions.quantity, "potion": potions.quantity}])
                elif potions.potion_type == [25,25,25,25]:
                    connection.execute(sqlalchemy.text
                    ("INSERT INTO shop_ledger (red_ml_change, green_ml_change, blue_ml_change, dark_ml_change, unmarked_potion_change, customer_name) VALUES (:ml_red, :ml_green, :ml_blue, :ml_dark, :potion, 'Shop')"),
                    [{"ml_red": -potions.potion_type[0] * potions.quantity, "ml_green": -potions.potion_type[1] * potions.quantity, "ml_blue": -potions.potion_type[2] * potions.quantity, "ml_dark": -potions.potion_type[3] * potions.quantity, "potion": potions.quantity}])
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
    MAX = 30
    with db.engine.begin() as connection:
        capacity = connection.execute(sqlalchemy.text("SELECT potion_capacity FROM global_inventory")).scalar_one()
        ledger = connection.execute(sqlalchemy.text
        ("SELECT SUM(red_ml_change) AS red_ml_change, SUM(green_ml_change) AS green_ml_change, SUM(blue_ml_change) AS blue_ml_change, SUM(dark_ml_change) AS dark_ml_change, SUM(red_potion_change) AS red_potion_change, SUM(green_potion_change) AS green_potion_change, SUM(blue_potion_change) AS blue_potion_change, SUM(dark_potion_change) AS dark_potion_change, SUM(purple_potion_change) AS purple_potion_change, SUM(forest_potion_change) AS forest_potion_change, SUM(navy_potion_change) AS navy_potion_change, SUM(maroon_potion_change) AS maroon_potion_change, SUM(unmarked_potion_change) AS unmarked_potion_change FROM shop_ledger WHERE customer_name = 'Shop'"))
        green_ml = 0
        red_ml = 0
        blue_ml = 0
        dark_ml = 0
        red_potion = 0
        green_potion = 0
        blue_potion = 0
        dark_potion = 0
        purple_potion = 0
        forest_potion = 0
        navy_potion = 0
        maroon_potion = 0
        unmarked_potion = 0
        total_potions = 0
        for row in ledger:
            green_ml = row.green_ml_change
            red_ml = row.red_ml_change
            blue_ml = row.blue_ml_change
            dark_ml = row.dark_ml_change
            red_potion = row.red_potion_change
            green_potion = row.green_potion_change
            blue_potion = row.blue_potion_change
            dark_potion = row.dark_potion_change
            purple_potion = row.purple_potion_change
            forest_potion = row.forest_potion_change
            navy_potion = row.navy_potion_change
            maroon_potion = row.maroon_potion_change
            unmarked_potion = row.unmarked_potion_change
            total_potions = row.red_potion_change + row.green_potion_change + row.blue_potion_change + row.dark_potion_change + row.purple_potion_change + row.forest_potion_change + row.navy_potion_change + row.maroon_potion_change + row.unmarked_potion_change

        # bottle no potions if ml not sufficient
        bottle_plan = []

        if total_potions < capacity:
            if red_ml >= 50 and blue_ml >= 50 and purple_potion < MAX:
                # bottle purple
                total = min(red_ml // 50, blue_ml // 50)
                if  total < MAX and total + total_potions <= capacity:
                    # bottle as many as possible without going over the max and capacity
                    bottle_plan.append({
                        "potion_type": [50, 0, 50, 0],
                        "quantity": total,
                    })
                    red_ml -= 50 * total
                    blue_ml -= 50 * total
                    total_potions += total
                elif total_potions + MAX <= capacity:
                    # bottle the max since given ml can make more
                    bottle_plan.append({
                        "potion_type": [50, 0, 50, 0],
                        "quantity": MAX,
                    })
                    red_ml -= 50 * MAX
                    blue_ml -= 50 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < total:
                    # bottle to fill capacity without over bottling
                    bottle_plan.append({
                        "potion_type": [50, 0, 50, 0],
                        "quantity": capacity - total_potions,
                    })
                    red_ml -= 50 * (capacity - total_potions)
                    blue_ml -= 50 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)
                

            if blue_ml >= 50 and dark_ml >= 50 and navy_potion < MAX:
                # bottle navy
                total = min(blue_ml // 50, dark_ml // 50)
                if total < MAX and total + total_potions <= capacity: 
                    bottle_plan.append({
                        "potion_type": [0, 0, 50, 50],
                        "quantity": total,
                    })
                    blue_ml -= 50 * total
                    dark_ml -= 50 * total
                    total_potions += total
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 0, 50, 50],
                        "quantity": MAX,
                    })
                    blue_ml -= 50 * MAX
                    dark_ml -= 50 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < total:
                    bottle_plan.append({
                        "potion_type": [0, 0, 50, 50],
                        "quantity": capacity - total_potions,
                    })
                    blue_ml -= 50 * (capacity - total_potions)
                    dark_ml -= 50 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)
                
            
            if red_ml >= 50 and dark_ml >= 50 and maroon_potion < MAX:
                # bottle maroon
                total = min(red_ml // 50, dark_ml // 50)
                if total < MAX and total + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [50, 0, 0, 50],
                        "quantity": total,
                    })
                    red_ml -= 50 * total
                    dark_ml -= 50 * total
                    total_potions += total
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [50, 0, 0, 50],
                        "quantity": MAX,
                    })
                    red_ml -= 50 * MAX
                    dark_ml -= 50 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < total:
                    bottle_plan.append({
                        "potion_type": [50, 0, 0, 50],
                        "quantity": capacity - total_potions,
                    })
                    red_ml -= 50 * (capacity - total_potions)
                    dark_ml -= 50 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if green_ml >= 50 and dark_ml >= 50 and forest_potion < MAX:
                # bottle forest
                total = min(green_ml // 50, dark_ml // 50)
                if total < MAX and total + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 50, 0, 50],
                        "quantity": total,
                    })
                    green_ml -= 50 * total
                    dark_ml -= 50 * total
                    total_potions += total
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 50, 0, 50],
                        "quantity": MAX,
                    })
                    green_ml -= 50 * MAX
                    dark_ml -= 50 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < total:
                    bottle_plan.append({
                        "potion_type": [0, 50, 0, 50],
                        "quantity": capacity - total_potions,
                    })
                    green_ml -= 50 * (capacity - total_potions)
                    dark_ml -= 50 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if red_ml >= 25 and green_ml >= 25 and blue_ml >= 25 and dark_ml >= 25 and unmarked_potion < MAX:
                # bottle useless
                total = min(red_ml // 25, green_ml // 25, blue_ml // 25, dark_ml // 25)
                if total < MAX and total + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [25, 25, 25, 25],
                        "quantity": total,
                    })
                    red_ml -= 25 * total
                    green_ml -= 25 * total
                    blue_ml -= 25 * total
                    dark_ml -= 25 * total
                    total_potions += total
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [25, 25, 25, 25],
                        "quantity": MAX,
                    })
                    red_ml -= 25 * MAX
                    green_ml -= 25 * MAX
                    blue_ml -= 25 * MAX
                    dark_ml -= 25 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < total:
                    bottle_plan.append({
                        "potion_type": [25, 25, 25, 25],
                        "quantity": capacity - total_potions,
                    })
                    red_ml -= 25 * (capacity - total_potions)
                    green_ml -= 25 * (capacity - total_potions)
                    blue_ml -= 25 * (capacity - total_potions)
                    dark_ml -= 25 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if green_ml >= 100 and green_potion < MAX:
                # bottle only green
                if green_ml // 100 < 25 and green_ml // 100 + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 100, 0, 0],
                        "quantity": green_ml // 100,
                    })
                    green_ml -= 100 * green_ml // 100
                    total_potions += green_ml // 100
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 100, 0, 0],
                        "quantity": MAX,
                    })
                    green_ml -= 100 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < green_ml // 100:
                    bottle_plan.append({
                        "potion_type": [0, 100, 0, 0],
                        "quantity": capacity - total_potions,
                    })
                    green_ml -= 100 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if red_ml >= 100 and red_potion < MAX:
                # bottle only red
                if red_ml // 100 < 20 and red_ml // 100 + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [100, 0, 0, 0],
                        "quantity": red_ml // 100,
                    })
                    red_ml -= 100 * red_ml // 100
                    total_potions += red_ml // 100
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [100, 0, 0, 0],
                        "quantity": MAX,
                    })
                    red_ml -= 100 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < red_ml // 100:
                    bottle_plan.append({
                        "potion_type": [100, 0, 0, 0],
                        "quantity": capacity - total_potions,
                    })
                    red_ml -= 100 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if blue_ml >= 100 and blue_potion < MAX:
                # bottle only blue
                if blue_ml // 100 < 20 and blue_ml // 100 + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 0, 100, 0],
                        "quantity": blue_ml // 100,
                    })
                    blue_ml -= 100 * blue_ml // 100
                    total_potions += blue_ml // 100
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 0, 100, 0],
                        "quantity": MAX,
                    })
                    blue_ml -= 100 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < blue_ml // 100:
                    bottle_plan.append({
                        "potion_type": [0, 0, 100, 0],
                        "quantity": capacity - total_potions,
                    })
                    blue_ml -= 100 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)

            if dark_ml >= 100 and dark_potion < MAX:
                # bottle only dark
                if dark_ml // 100 < 20 and dark_ml // 100 + total_potions <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 0, 0, 100],
                        "quantity": dark_ml // 100,
                    })
                    dark_ml -= 100 * dark_ml // 100
                    total_potions += dark_ml // 100
                elif total_potions + MAX <= capacity:
                    bottle_plan.append({
                        "potion_type": [0, 0, 0, 100],
                        "quantity": MAX,
                    })
                    dark_ml -= 100 * MAX
                    total_potions += MAX
                elif capacity - total_potions > 0 and capacity - total_potions < dark_ml // 100:
                    bottle_plan.append({
                        "potion_type": [0, 0, 0, 100],
                        "quantity": capacity - total_potions,
                    })
                    dark_ml -= 100 * (capacity - total_potions)
                    total_potions += (capacity - total_potions)
                

    print(f"Current bottle plan: {bottle_plan}" )

    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())