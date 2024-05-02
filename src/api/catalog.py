from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price. 6 potions at a time
    """
    with db.engine.begin() as connection:
        potions = connection.execute(sqlalchemy.text("SELECT sku, type, price, quantity FROM potion_inventory"))
        ledger = connection.execute(sqlalchemy.text("SELECT SUM(red_potion_change) AS red_potion_change, SUM(green_potion_change) AS green_potion_change, SUM(blue_potion_change) AS blue_potion_change, SUM(dark_potion_change) AS dark_potion_change, SUM(purple_potion_change) AS purple_potion_change, SUM(forest_potion_change) AS forest_potion_change, SUM(navy_potion_change) AS navy_potion_change, SUM(maroon_potion_change) AS maroon_potion_change, SUM(unmarked_potion_change) AS unmarked_potion_change FROM shop_ledger WHERE customer_name = 'Shop'"))
        catalog = []
        for quantity in ledger:
            for row in potions: 
                if row.sku == "RED_POTION" and quantity.red_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Health",
                            "quantity": quantity.red_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "GREEN_POTION" and quantity.green_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Leap",
                            "quantity": quantity.green_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "BLUE_POTION" and quantity.blue_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Swiftness I",
                            "quantity": quantity.blue_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "DARK_POTION" and quantity.dark_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Invisibility",
                            "quantity": quantity.dark_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "PURPLE_POTION" and quantity.purple_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Teleportation",
                            "quantity": quantity.purple_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "FOREST_POTION" and quantity.forest_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Swiftness II",
                            "quantity": quantity.forest_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "NAVY_POTION" and quantity.navy_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Night Vision",
                            "quantity": quantity.navy_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "MAROON_POTION" and quantity.maroon_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "Regeneration",
                            "quantity": quantity.maroon_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
                if row.sku == "UNMARKED_POTION" and quantity.unmarked_potion_change > 0:
                    catalog.append(            {
                            "sku": row.sku,
                            "name": "???",
                            "quantity": quantity.unmarked_potion_change,
                            "price": row.price,
                            "potion_type": row.type,
                        })
        if len(catalog) > 6:
            catalog = catalog[:6]

    return catalog
