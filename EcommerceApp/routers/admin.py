from fastapi import APIRouter,Depends,HTTPException,Path
from ..models import Users
from sqlalchemy.orm import Session
from ..database import  SessionLocal
from typing import Annotated
from starlette import status
from .auth import get_current_user


router=APIRouter(prefix='/admin',
    tags=['admin'])



def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.get("/users/",status_code=status.HTTP_200_OK)
async def read_all_user(user:user_dependency,db:db_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return db.query(Users).all()

@router.get("/user/{user_id}",status_code=status.HTTP_200_OK)
async def read_user(user:user_dependency,db:db_dependency,user_id:int =Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user_id).first()

@router.delete("/user/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user:user_dependency,db:db_dependency,user_id:int =Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')

    if user_id == user.get('id'):
        raise HTTPException(status_code=400,detail='Cannot delete admin.')

    user_model=db.query(Users).filter(Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404,detail='User not found.')
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()