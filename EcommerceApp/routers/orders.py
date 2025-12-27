from fastapi import APIRouter, HTTPException, Path
from ..models.products_model import Products
from EcommerceApp.models.carts_model import Carts
from EcommerceApp.models.orders_model import Orders,OrderItems
from starlette import status
from .auth import user_dependency,db_dependency
from ..schemas.orders_schema import OrderResponse,UpdateOrderStatus

router=APIRouter(prefix='/orders',tags=['orders'])

@router.post("/checkout",status_code=status.HTTP_201_CREATED)
async def checkout(user:user_dependency,
                   db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')

    cart_items=db.query(Carts).filter(Carts.user_id == user.get('id')).all()
    if not cart_items:
        raise HTTPException(status_code=400,detail='Your Cart is currently empty!')

    try:
        new_order=Orders(
            user_id=user.get('id'),
            total_amount=0,
            status='pending',
        )
        db.add(new_order)
        db.flush()

        total_amount=0

        for cart_item in cart_items:
            product=db.query(Products).filter(Products.id == cart_item.product_id).first()
            if not product or product.stock < cart_item.quantity:
                raise HTTPException(status_code=401,detail=f"Product {product.title if product else 'ID'+str(cart_item.product_id)} out of stock.")

            product.stock -= cart_item.quantity
            item_price=product.price
            total_amount += item_price * cart_item.quantity

            order_item=OrderItems(
                order_id=new_order.id,
                product_id=product.id,
                price_at_purchase=item_price,
                quantity=cart_item.quantity,
            )
            db.add(order_item)
        new_order.total_amount=total_amount
        db.query(Carts).filter(Carts.user_id == user.get('id')).delete()
        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Error while processing checkout!")


@router.get("/",status_code=status.HTTP_200_OK,response_model=list[OrderResponse])
async def checkout_history(user:user_dependency,
                           db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')

    order_model=db.query(Orders)\
        .filter(Orders.user_id == user.get('id'))\
        .order_by(Orders.created_at.desc())\
        .all()
    return order_model

@router.get("/admin/{order_id}",status_code=status.HTTP_200_OK,response_model=OrderResponse)
async def admin_checkout(user:user_dependency,
                         db:db_dependency,
                         order_id:int= Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=403,detail='You do not have permission to access this.')
    order_model=db.query(Orders)\
    .filter(Orders.id == order_id)\
    .first()
    if not order_model:
        raise HTTPException(status_code=404,detail='Order not found.')
    return order_model

@router.put("/admin/{order_id}/status",status_code=status.HTTP_200_OK,response_model=OrderResponse)
async def update_order_status(user:user_dependency,
                              db:db_dependency,
                              request:UpdateOrderStatus
                              ,order_id:int= Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=403,detail='You do not have permission to access this.')

    order_model=db.query(Orders)\
    .filter(Orders.id == order_id).first()
    if not order_model:
        raise HTTPException(status_code=404, detail='Order not found.')
    order_model.status=request.status
    db.add(order_model)
    db.commit()
    db.refresh(order_model)
    return order_model

@router.put("/{order_id}/cancel",status_code=status.HTTP_200_OK)
async def cancel_order(user:user_dependency,
                                db:db_dependency
                                ,order_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')
    order_model = db.query(Orders) \
        .filter(Orders.id == order_id).first()
    if not order_model:
        raise HTTPException(status_code=404, detail='Order not found.')
    if user.get('user_role')!='admin' and order_model.user_id!=user.get('id'):
        raise HTTPException(status_code=403,detail='You do not have permission to cancel this order.')
    if order_model.status !='pending':
        raise HTTPException(status_code=400,detail=f"You cannot cancel this order anymore.This order is already {order_model.status}")
    try:
        for item in order_model.items:
            product=db.query(Products).filter(Products.id == item.product_id).first()
            if product:
                product.stock += item.quantity
                db.add(product)

        order_model.status='cancelled'
        db.add(order_model)
        db.commit()
        return {'detail':'Successfully Cancelled Order!'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error while trying cancel order!")





