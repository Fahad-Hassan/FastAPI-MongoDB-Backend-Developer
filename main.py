from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List

app = FastAPI()

# MongoDB setup
client = AsyncIOMotorClient("mongodb+srv://FAST_API_TEST:EeDabC6Js8xEzOBm@cluster0.iynsonj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["fastapi_db"]
collection = db["items"]
if(db.connection is None):
    raise Exception("Failed to connect to MongoDB")

# Helper to convert ObjectId
def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item["description"],
        "price": item["price"]
    }

# Pydantic model
class Item(BaseModel):
    name: str
    description: str
    price: float

# Create item
@app.post("/items", response_model=dict)
async def create_item(item: Item):
    result = await collection.insert_one(item.dict())
    new_item = await collection.find_one({"_id": result.inserted_id})
    return item_helper(new_item)

# Get all items
@app.get("/items", response_model=List[dict])

async def get_items():
    items = []
    async for item in collection.find():
        items.append(item_helper(item))
    return items

# Get item by ID
@app.get("/items/{item_id}", response_model=dict)
async def get_item(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(item)

# Update item
@app.put("/items/{item_id}", response_model=dict)
async def update_item(item_id: str, item: Item):
    update_result = await collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item.dict()}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await collection.find_one({"_id": ObjectId(item_id)})
    return item_helper(updated_item)

# Delete item
@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: str):
    result = await collection.find_one_and_delete({"_id": ObjectId(item_id)})
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(result)


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI MongoDB example!"}
# Run the application with: uvicorn main:app --reload


