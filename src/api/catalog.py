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
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        catalog = []
        for row in result: 
            if row.sku == "RED_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Health",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "GREEN_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Leap",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "BLUE_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Swiftness I",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "DARK_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Invisibility",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "PURPLE_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Teleportation",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "FOREST_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Swiftness II",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "NAVY_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Night Vision",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "MAROON_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "Regeneration",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            if row.sku == "UNMARKED_POTION" and row.quantity > 0:
                catalog.append(            {
                        "sku": row.sku,
                        "name": "???",
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })

    return catalog
