from fastapi import HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from starlette import status
from models import Todos
from database import db_dependency

todosRouter = APIRouter()

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=3)
    completed: bool = False

@todosRouter.get("/todos", status_code= status.HTTP_200_OK)
def get_todos(db: db_dependency):
    todos = db.query(Todos).all()

    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")

    return todos

@todosRouter.get("/todos/{id}", status_code=status.HTTP_200_OK)
def get_todo(db: db_dependency, todo_id: int):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is not None:
        return todo

    raise HTTPException(
        status_code=404,
        detail="No todo found with the given id"
    )

@todosRouter.post("/todos", status_code=status.HTTP_201_CREATED)
def create_new_todo(db: db_dependency, todoRequest: TodoRequest):
    todo_model = Todos(**todoRequest.model_dump())

    db.add(todo_model)
    db.commit()

@todosRouter.put("/todos/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_todo(
        db: db_dependency,
        todoRequest: TodoRequest,
        todo_id: int = Path(gt=0),):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="No todo found with the given id"
        )

    # todo = Todos(**todoRequest.model_dump())

    todo.title = todoRequest.title
    todo.description = todoRequest.description
    todo.priority = todoRequest.priority
    todo.completed = todoRequest.completed

    db.add(todo)
    db.commit()

@todosRouter.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="No todo found with the given id"
        )

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()