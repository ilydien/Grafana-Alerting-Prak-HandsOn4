from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.data_generator import generate_transactions

app = FastAPI(title="Online Store Financial Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/transactions")
def get_transactions():
    data = generate_transactions(60)
    return data
