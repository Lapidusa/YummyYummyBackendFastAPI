import logging
from sqlalchemy.future import select

from app.core.config import settings
from app.db.models.users import User, Roles

logger = logging.getLogger(__name__)

ADMIN_PHONE = settings.ADMIN_PHONE

async def create_admin(session):
    result = await session.execute(select(User).filter(User.phone_number == ADMIN_PHONE))
    admin = result.scalars().first()
    if not admin:
        admin = User(phone_number=ADMIN_PHONE, role=Roles.ADMIN)
        session.add(admin)
        await session.commit()
        logger.info(f"Admin user created with phone number: {ADMIN_PHONE}")
    else:
        logger.info(f"Admin user already exists with phone number: {ADMIN_PHONE}")
