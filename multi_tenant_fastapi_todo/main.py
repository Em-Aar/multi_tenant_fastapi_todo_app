from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select
from typing import Annotated
from contextlib import asynccontextmanager
from multi_tenant_fastapi_todo.auth import ACCESS_TOKE_EXPIRE_MINUTE, Token, authenticate_user, create_access_token, get_current_user
from multi_tenant_fastapi_todo.db import User, engine, Todo, get_session
from multi_tenant_fastapi_todo.router import user


def create_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Creating Tables')
    create_tables()
    print("Tables Created")
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan, title="dailyDo Todo App", version='1.0.0')


app.include_router(router=user.user_router)


@app.get('/')
async def root():
    return {"message": "Welcome to dailyDo todo app"}


@app.post('/token')
async def login(user: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Annotated[Session, Depends(get_session)]
                ):
    user_from_db = authenticate_user(user.username, user.password, session)
    if not user_from_db:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKE_EXPIRE_MINUTE)
    access_token = create_access_token(
        data={"sub": user_from_db.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post('/todos/', response_model=Todo)
async def create_todo(current_user: Annotated[User,Depends(get_current_user)],
                      todo: Todo,
                      session: Annotated[Session, Depends(get_session)]
                      ):
    todo.user_id = current_user.id
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.get('/todos/', response_model=list[Todo])
async def get_all(current_user: Annotated[User, Depends(get_current_user)],
                  session: Annotated[Session, Depends(get_session)]
                  ):
    todos = session.exec(select(Todo).where(
        Todo.user_id == current_user.id)).all()
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No Task found")


@app.get('/todos/{id}', response_model=Todo)
async def get_single_todo(id: int,
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]
                          ):
    # todo = session.exec(select(Todo).where(
    #     Todo.user_id == current_user.id and Todo.id == id)).first()
    
    user_todos = session.exec(select(Todo).where(
        Todo.user_id == current_user.id
    ))
    matched_todo = next((todo for todo in user_todos if todo.id == id), None)

    if matched_todo:
        return matched_todo
    else:
        raise HTTPException(status_code=404, detail="No Task found")


@app.put('/todos/{id}')
async def edit_todo(id: int, 
                    todo: Todo,
                    current_user: Annotated[User, Depends(get_current_user)], 
                    session: Annotated[Session, Depends(get_session)]
                    ):
    
    user_todos = session.exec(select(Todo).where(
        Todo.user_id == current_user.id
    ))
    existing_matched_todo = next((todo for todo in user_todos if todo.id == id), None)
    
    # existing_todo = session.exec(select(Todo).where(Todo.id == id and Todo.user_id == current_user.id)).first()
    if existing_matched_todo:
        existing_matched_todo.content = todo.content
        existing_matched_todo.is_completed = todo.is_completed
        session.add(existing_matched_todo)
        session.commit()
        session.refresh(existing_matched_todo)
        return existing_matched_todo
    else:
        raise HTTPException(status_code=404, detail="No task found")


@app.delete('/todos/{id}')
async def delete_todo(id: int,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]
                      ):
    todo = session.exec(select(Todo).where(Todo.id == id and Todo.user_id == get_current_user.id)).first()
    if todo:
        session.delete(todo)
        session.commit()
        return {"message": "Task successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="No task found")
