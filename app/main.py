from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, message, group
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

app.include_router(user.userRouter().router)
app.include_router(message.messageRouter().router)
app.include_router(group.groupRouter().router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)