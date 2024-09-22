from fastapi import FastAPI,Request,HTTPException
from  .routers import users, service
from .database import engine
from .models import Base
import sys
Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(users.router)
app.include_router(service.router)
