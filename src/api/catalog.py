from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        green_potions = 0
        red_potions = 0
        blue_potions = 0
        dark_potions = 0
        for row in result:
            green_potions = row.num_green_potions
            red_potions = row.num_red_potions
            blue_potions = row.num_blue_potions
            dark_potions = row.num_dark_potions
    catalog = []
    if red_potions > 0:
        catalog.append(            {
                "sku": "RED_POTIONS_0",
                "name": "red potion",
                "quantity": red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            })
    if green_potions > 0:
        catalog.append(            {
                "sku": "GREEN_POTIONS_0",
                "name": "green potion",
                "quantity": green_potions,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            })
    if blue_potions > 0:
        catalog.append(            {
                "sku": "BLUE_POTIONS_0",
                "name": "blue potion",
                "quantity": blue_potions,
                "price": 50,
                "potion_type": [0, 0, 100, 0],
            })
    if dark_potions > 0:
        catalog.append(            {
                "sku": "DARK_POTIONS_0",
                "name": "dark potion",
                "quantity": dark_potions,
                "price": 50,
                "potion_type": [0, 0, 0, 100],
            })

    return catalog
