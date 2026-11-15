from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import Product, User
from mysite.database.schema import ProductInputSchema, ProductUpdateSchema, ProductOutputSchema
from mysite.api.auth import get_db, get_current_user

product_router = APIRouter(prefix='/product', tags=['Product'])


@product_router.post('/', response_model=ProductOutputSchema)
async def product_create(product: ProductInputSchema, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    product_db = Product(**product.model_dump())
    db.add(product_db)
    db.commit()
    db.refresh(product_db)
    return product_db


@product_router.get('/', response_model=List[ProductOutputSchema])
async def product_list(db: Session = Depends(get_db)):
    return db.query(Product).all()


@product_router.get('/{product_id}/', response_model=ProductOutputSchema)
async def product_detail(product_id: int, db: Session = Depends(get_db)):
    product_db = db.query(Product).filter(Product.id == product_id).first()
    if not product_db:
        raise HTTPException(detail='Такого продукта нету', status_code=404)
    return product_db


@product_router.put('/{product_id}/', response_model=dict)
async def product_update(product_id: int, product: ProductUpdateSchema, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    product_db = db.query(Product).filter(Product.id == product_id).first()
    if not product_db:
        raise HTTPException(detail='Такого продукта нету', status_code=404)

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(product_db, key, value)

    db.commit()
    db.refresh(product_db)
    return {'message': 'Продукт изменён'}


@product_router.delete('/{product_id}/', response_model=dict)
async def product_delete(product_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    product_db = db.query(Product).filter(Product.id == product_id).first()
    if not product_db:
        raise HTTPException(detail='Такого продукта нету', status_code=404)

    db.delete(product_db)
    db.commit()
    return {'message': 'Продукт удалён'}