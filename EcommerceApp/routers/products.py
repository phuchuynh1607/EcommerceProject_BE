from fastapi import APIRouter, HTTPException, Path, Body

from ..models.orders_model import Orders, OrderItems
from ..schemas.products_schema import ProductRequest
from EcommerceApp.models.products_model import Products
from starlette import status
from .auth import user_dependency,db_dependency
from typing import List, Optional

router=APIRouter(prefix='/products',tags=['products'])




@router.get("/",status_code=status.HTTP_200_OK)
async def read_all_products(db:db_dependency,category: Optional[str] = None,search: Optional[str] = None):
    query=db.query(Products)
    if category:
        query = query.filter(Products.category.ilike(category))
    if search:
        query = query.filter(Products.title.ilike(f"{search}%"))
    return query.all()

@router.get("/product/{product_id}",status_code=status.HTTP_200_OK)
async def read_product(db:db_dependency,product_id:int =Path(gt=0)):
    product=db.query(Products).filter(Products.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404,detail="Can't find product!")
    return product


@router.post("/product", status_code=status.HTTP_201_CREATED)
async def create_product(user: user_dependency, db: db_dependency, product_request: ProductRequest):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=403, detail='You do not have permission to access this.')

    # Trích xuất dữ liệu từ Schema lồng nhau sang Model phẳng
    product_model = Products(
        title=product_request.title,
        price=product_request.price,
        description=product_request.description,
        category=product_request.category,
        image=product_request.image,
        stock=product_request.stock,
        rate=product_request.rating.rate,
        count=product_request.rating.count
    )

    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_multiple_products(db: db_dependency, user: user_dependency, products: List[ProductRequest]):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=403, detail='Permission denied.')

    product_models = []
    for p in products:

        model = Products(
            title=p.title,
            price=p.price,
            description=p.description,
            category=p.category,
            image=p.image,
            stock=p.stock,
            rate=p.rating.rate,
            count=p.rating.count
        )
        product_models.append(model)

    db.add_all(product_models)
    db.commit()
    return {"message": f"Successfully added {len(product_models)} products"}
@router.put("/product/{product_id}",status_code=status.HTTP_200_OK)
async def update_product(user:user_dependency,
                         db:db_dependency
                         ,product_request:ProductRequest
                         ,product_id:int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=403,detail='You do not have permission to access this.')

    product_model=db.query(Products).filter(Products.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail="Can't find product!")


    update_data = product_request.model_dump(exclude_unset=True)


    for key, value in update_data.items():
        setattr(product_model, key, value)

    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model

@router.delete("/delete/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(user:user_dependency
                         ,db:db_dependency
                         ,product_id:int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=403,detail='You do not have permission to access this.')

    product_model=db.query(Products).filter(Products.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail="Can't find product!")

    db.delete(product_model)
    db.commit()

@router.put("/product/{product_id}/rating", status_code=status.HTTP_200_OK)
async def rate_product(
    user: user_dependency,
    db: db_dependency,
    product_id: int = Path(gt=0),
    new_star: int = Body(ge=1, le=5)
):
    # 1. Kiểm tra đăng nhập
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )

    # 2. Kiểm tra quyền: Đã mua và đơn hàng ở trạng thái 'completed' chưa?
    # Logic: Join bảng Orders và OrderItems để check
    purchase_verified = db.query(Orders).join(OrderItems).filter(
        Orders.user_id == user.get('id'),
        OrderItems.product_id == product_id,
        Orders.status == "completed"
    ).first()

    if not purchase_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể đánh giá sản phẩm sau khi đã mua và nhận hàng thành công."
        )

    # 3. Tìm sản phẩm để cập nhật logic rating
    product_model = db.query(Products).filter(Products.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found!")

    # 4. Tính toán rating trung bình tích lũy (Không cần bảng Review)
    current_rating = product_model.rating or 0
    current_count = product_model.review_count or 0

    new_count = current_count + 1

    updated_rating = ((current_rating * current_count) + new_star) / new_count

    # 5. Cập nhật vào model
    product_model.rating = round(updated_rating, 1)
    product_model.review_count = new_count

    db.add(product_model)
    db.commit()
    db.refresh(product_model)

    return {
        "message": f"You've rated this product {new_star}",
        "your_rating": new_star,
        "new_rating": product_model.rating,
        "review_count": product_model.review_count
    }