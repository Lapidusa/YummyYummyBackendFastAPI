from fastapi import APIRouter
from app.routers.user import router as user_router
from app.routers.city import router as city_router
from app.routers.store import router as store_router
from app.routers.category import router as category_router
from app.routers.product import router as product_router

main_router = APIRouter()
main_router.include_router(user_router, prefix="/user", tags=["User"])
main_router.include_router(city_router, prefix="/city", tags=["City"])
main_router.include_router(store_router, prefix="/store", tags=["Store"])
main_router.include_router(category_router, prefix="/category", tags=["Category"])
main_router.include_router(product_router, prefix="/product", tags=["Product"])