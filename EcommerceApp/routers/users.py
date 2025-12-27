from fastapi import APIRouter,HTTPException
from EcommerceApp.models.users_model import Users
from starlette import status
from .auth import user_dependency,db_dependency, bcrypt_context
from ..schemas.users_schema import UserVerification,UserUpdateRequest,UserResponse
router = APIRouter(prefix='/users',tags=['users'])







@router.get("/",status_code=status.HTTP_200_OK,response_model=UserResponse)
async def get_user_information(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency,db:db_dependency,user_verification:UserVerification):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    user_model =db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password,user_model.hashed_password):
        raise HTTPException(status_code=401,detail='Error on password change')
    user_model.hashed_password= bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/change_information",status_code=status.HTTP_200_OK,response_model=UserResponse)
async def change_user_information(user:user_dependency
                                  ,db:db_dependency
                                  ,user_request:UserUpdateRequest):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    user_model=db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.first_name = user_request.first_name
    user_model.last_name = user_request.last_name
    user_model.phone_number = user_request.phone_number

    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model
