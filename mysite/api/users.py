from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import User
from mysite.database.schema import UserUpdateSchema, UserOutputSchema, UserShortSchema
from mysite.api.auth import get_db, get_current_user, get_password_hash

user_router = APIRouter(prefix='/users', tags=['Users'])


def check_owner(user_id: int, current_user: User):
    # башка адамдын аккаунтуна тийүүгө болбойт
    if current_user.id != user_id:
        raise HTTPException(detail='К такому действию нету прав', status_code=403)


@user_router.get('/', response_model=List[UserShortSchema])
async def user_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()


@user_router.get('/{user_id}/', response_model=UserOutputSchema)
async def user_detail(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    check_owner(user_id, current_user)
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(detail='Такого акканута нету', status_code=404)
    return user_db


@user_router.put('/{user_id}/', response_model=dict)
async def user_update(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    check_owner(user_id, current_user)
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(detail='Такого аккаунта нету', status_code=404)

    data = user.model_dump(exclude_unset=True)

    # username/email башка адамда болбошу керек
    if data.get('username'):
        exists = db.query(User).filter(User.username == data['username'], User.id != user_id).first()
        if exists:
            raise HTTPException(detail='Такой username уже есть', status_code=400)
    if data.get('email'):
        exists = db.query(User).filter(User.email == data['email'], User.id != user_id).first()
        if exists:
            raise HTTPException(detail='Такой email уже есть', status_code=400)
    if 'password' in data:
        data['password'] = get_password_hash(data['password'])   # пароль хэш болуп сакталат

    for key, value in data.items():
        setattr(user_db, key, value)

    db.commit()
    db.refresh(user_db)
    return {'message': 'Информация изменена'}


@user_router.delete('/{user_id}/', response_model=dict)
async def user_delete(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  # check_owner(user_id, current_user)  <-- Закомментируйте эту строчку на время тестов
  user_db = db.query(User).filter(User.id == user_id).first()
  if not user_db:
    raise HTTPException(detail='Такого аккаунта нету', status_code=404)

  db.delete(user_db)
  db.commit()
  return {'message': 'Аккаунт удалён'}