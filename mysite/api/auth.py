from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from typing import Optional

from mysite.database.models import User, RefreshToken
from mysite.database.schema import (
    UserRegisterSchema, UserLoginSchema, UserOutputSchema, RefreshTokenSchema
)
from mysite.database.db import SessionLocal
from mysite.config import SECRET_KEY

ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = 30
REFRESH_TOKEN_LIFETIME = 7

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
bearer_schema = HTTPBearer()

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, token_type: str, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update({
        'exp': datetime.now(timezone.utc) + expires_delta,
        'type': token_type            # 'access' же 'refresh'
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return create_token(data, 'access', expires_delta or timedelta(minutes=ACCESS_TOKEN_LIFETIME))


def create_refresh_token(data: dict):
    return create_token(data, 'refresh', timedelta(days=REFRESH_TOKEN_LIFETIME))


def decode_token(token: str, token_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail='Токен не исправен или истек время')
    if payload.get('type') != token_type:
        raise HTTPException(status_code=401, detail='Нерпаивльный вид токена')
    return payload


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_schema),
                           db: Session = Depends(get_db)):
    payload = decode_token(credentials.credentials, 'access')
    user_db = db.query(User).filter(User.username == payload.get('sub')).first()
    if not user_db:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    return user_db


# ---------- endpoints ----------
@auth_router.post('/register/', response_model=dict)
async def register(user: UserRegisterSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == user.username).first()
    email_db = db.query(User).filter(User.email == user.email).first()
    if user_db or email_db:
        raise HTTPException(detail='Такой username или email уже есть', status_code=400)

    user_data = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {'message': 'Вы успешно зарегстрировались'}


@auth_router.post('/login/', response_model=dict)
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == user.username).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(detail='Написанная вами информация неправильная', status_code=401)

    access_token = create_access_token({'sub': user_db.username})
    refresh_token = create_refresh_token({'sub': user_db.username})

    db.add(RefreshToken(user_id=user_db.id, token=refresh_token))
    db.commit()

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}


@auth_router.post('/refresh/', response_model=dict)
async def refresh(request: RefreshTokenSchema, db: Session = Depends(get_db)):
    decode_token(request.refresh_token, 'refresh')
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Инфромация не верна')

    user_db = db.query(User).filter(User.id == stored_token.user_id).first()
    if not user_db:
        raise HTTPException(status_code=401, detail='Такого пользователя нету')

    access_token = create_access_token({'sub': user_db.username})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@auth_router.post('/logout/', response_model=dict)
async def logout(request: RefreshTokenSchema, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Информация непрвильно')

    db.delete(stored_token)
    db.commit()
    return {'message': 'Успешно вышли с аккаунта'}


@auth_router.get('/me/', response_model=UserOutputSchema)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.get('/verify/', response_model=dict)
async def verify(current_user: User = Depends(get_current_user)):
    # токен жарактуу болсо гана ушул жерге жетет
    return {'valid': True, 'username': current_user.username}