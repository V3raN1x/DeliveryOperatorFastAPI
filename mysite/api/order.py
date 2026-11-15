from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import Order, Product, User
from mysite.database.schema import OrderInputSchema, OrderUpdateSchema, OrderOutputSchema
from mysite.api.auth import get_db, get_current_user

order_router = APIRouter(prefix='/order', tags=['Order'])


def get_my_order(order_id: int, db: Session, current_user: User):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise HTTPException(detail='Такого заказа нету', status_code=404)
    if order_db.user_id != current_user.id:
        raise HTTPException(detail='Этот заказ не ваш', status_code=403)
    return order_db


@order_router.post('/', response_model=OrderOutputSchema)
async def order_create(order: OrderInputSchema, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    product_db = db.query(Product).filter(Product.id == order.product_id).first()
    if not product_db:
        raise HTTPException(detail='Такого продукта нету', status_code=404)

    order_db = Order(
        user_id=current_user.id,
        product_id=product_db.id,
        quantity=order.quantity,
        total_price=product_db.price * order.quantity,   # баасы өзү эсептелет
    )
    db.add(order_db)
    db.commit()
    db.refresh(order_db)
    return order_db


@order_router.get('/', response_model=List[OrderOutputSchema])
async def order_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@order_router.get('/{order_id}/', response_model=OrderOutputSchema)
async def order_detail(order_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    return get_my_order(order_id, db, current_user)


@order_router.put('/{order_id}/', response_model=dict)
async def order_update(order_id: int, order: OrderUpdateSchema, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    order_db = get_my_order(order_id, db, current_user)
    data = order.model_dump(exclude_unset=True)

    if data.get('quantity') is not None:
        if order_db.order_status != 'pending':
            raise HTTPException(detail='Заказ подтвержден, количество изменить нельзя', status_code=400)
        order_db.quantity = data['quantity']
        order_db.total_price = order_db.product.price * data['quantity']
    if data.get('order_status') is not None:
        order_db.order_status = data['order_status']

    db.commit()
    db.refresh(order_db)
    return {'message': 'Заказ өзгөрдү'}


@order_router.delete('/{order_id}/', response_model=dict)
async def order_delete(order_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    order_db = get_my_order(order_id, db, current_user)
    db.delete(order_db)
    db.commit()
    return {'message': 'Заказ удалён'}