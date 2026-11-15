from fastapi import FastAPI
import uvicorn
from mysite.api import users, auth, product, order, ai
from mysite.admin.setup import setup_admin
from mysite.database.db import Base, engine

Base.metadata.create_all(bind=engine)

delivery_app = FastAPI(title='Delivery Operator')

delivery_app.include_router(auth.auth_router)
delivery_app.include_router(users.user_router)
delivery_app.include_router(product.product_router)
delivery_app.include_router(order.order_router)
delivery_app.include_router(ai.ai_router)

setup_admin(delivery_app)

if __name__ == '__main__':
    uvicorn.run("main:delivery_app", host='127.0.0.1', port=8000, reload=True)