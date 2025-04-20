import logging

import uvicorn
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.routers.user import router as user_router
from app.routers.city import router as city_router
from app.routers.store import router as store_router
from app.core.config import settings
from app.db.models.users import User, Roles

load_dotenv(find_dotenv())
logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL
ADMIN_PHONE = settings.ADMIN_PHONE

engine = create_async_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI(default_response_class=ORJSONResponse)


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(city_router, prefix="/city", tags=["City"])
app.include_router(store_router, prefix="/store", tags=["Store"])

app.mount("/media", StaticFiles(directory="media"), name="media")
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "This is a backend service for Yummy Yummy!"}

async def create_admin(session: AsyncSession):
  result = await session.execute(select(User).filter(User.phone_number == ADMIN_PHONE))
  admin = result.scalars().first()
  if not admin:
    admin = User(phone_number=ADMIN_PHONE, role=Roles.ADMIN)
    session.add(admin)
    await session.commit()
    logger.info(f"Admin user created with phone number: {ADMIN_PHONE}")
  else:
    logger.info(f"Admin user already exists with phone number: {ADMIN_PHONE}")

@app.on_event("startup")
async def startup_event():
    async with SessionLocal() as session:
        await create_admin(session)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)