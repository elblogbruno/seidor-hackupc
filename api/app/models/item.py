from pydantic import BaseModel

class Item(BaseModel):
    ItemID: int
    Name: str
    Category: str
    Price: float

class User(BaseModel):
    UserID: int
    Name: str
    Email: str

class Order(BaseModel):
    OrderID: int
    UserID: int
    OrderDate: str
    TotalAmount: float

class Location(BaseModel):
    LocationID: int
    Aisle: int
    Shelf: int
    Bin: int

class ItemLocation(BaseModel):
    ItemLocationID: int
    ItemID: int
    LocationID: int
