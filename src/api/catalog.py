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
    num = 0
    for row in result:
        num = row.num_green_potions
    
    return [
            {
                "sku": "GREEN_POTIONS_0",
                "name": "green potion",
                "quantity": num,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
