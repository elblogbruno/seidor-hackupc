from fastapi import FastAPI
from api import routes
from typing import List, Optional, Union
from datetime import datetime
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()

app.include_router(routes.router)


class Product(BaseModel):
    id: Optional[Union[str, int]]
    name: str
    ean: Optional[Union[str, int]]
    quantity: Optional[int]

class Order(BaseModel):
    products: List[Product]

import os

def save_to_file(order: Order):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"order_{timestamp}.txt"
    folder = "orders"

    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)

    with open(filepath, "w") as f:
        for product in order.products:
            f.write(f"Product ID: {product.id}\n")
            f.write(f"Name: {product.name}\n")
            f.write(f"EAN: {product.ean}\n")
            f.write(f"Quantity: {product.quantity}\n\n")

@app.post("/save_order/")
async def save_order(order: Order):
    save_to_file(order)
    return {"message": "Order saved successfully"}

@app.get("/warehouse/")
async def get_warehouse_csv():
    # return products.csv on the same folder as main.py
    with open("warehouse.csv", "r") as f:
        return Response(content=f.read(), media_type="text/csv")

@app.get("/client/")
async def get_client_csv():
    # return products.csv on the same folder as main.py
    with open("products.csv", "r") as f:
        return Response(content=f.read(), media_type="text/csv")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)