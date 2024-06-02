from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from routers import name

app = FastAPI()

# app.include_router(name.routername.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)