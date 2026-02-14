import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Nexus Financial Ecosystem")

DB_FILE = "database.json"

# --- DATABASE LOGIC ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    # Default data if file doesn't exist
    return {
        "jane_doe": {"name": "Jane Doe", "balance": 1000.0, "history": []},
        "john_smith": {"name": "John Smith", "balance": 500.0, "history": []}
    }

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- MODELS ---
class TransferRequest(BaseModel):
    sender: str
    recipient: str
    amount: float

class CreateAccountRequest(BaseModel):
    username: str
    full_name: str
    initial_balance: float = 0.0

# --- ROUTES ---

@app.get("/")
def home():
    return {"status": "Ecosystem Online & Persistent"}

@app.post("/accounts")
def create_account(request: CreateAccountRequest):
    if request.username in db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db[request.username] = {
        "name": request.full_name,
        "balance": request.initial_balance,
        "history": [f"Account created on {datetime.now().strftime('%Y-%m-%d')}"]
    }
    save_db(db) # Save to file!
    return {"message": f"Account for {request.username} created!"}

@app.post("/transfer")
def transfer_money(request: TransferRequest):
    if request.sender not in db or request.recipient not in db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db[request.sender]["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Transaction
    db[request.sender]["balance"] -= request.amount
    db[request.recipient]["balance"] += request.amount

    # History
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db[request.sender]["history"].append(f"Sent ${request.amount} to {request.recipient} at {timestamp}")
    db[request.recipient]["history"].append(f"Received ${request.amount} from {request.sender} at {timestamp}")

    save_db(db) # Save to file!
    return {"message": "Transfer Successful"}

@app.get("/accounts/{username}")
def get_account(username: str):
    if username not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return db[username]