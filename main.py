import logging
import uvicorn
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.db.session import SessionLocal
from app.routers import main_router
from app.utils import create_admin

load_dotenv(find_dotenv())
logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(default_response_class=ORJSONResponse)

origins = ["http://localhost", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)

app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "This is a backend service for Yummy Yummy!"}

@app.on_event("startup")
async def startup_event():
    async with SessionLocal() as session:
        await create_admin(session)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)