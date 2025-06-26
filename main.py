from fastapi import FastAPI
import models
from database import engine
from router.auth import authRouter
from router.todos import todosRouter

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(todosRouter)
app.include_router(authRouter)