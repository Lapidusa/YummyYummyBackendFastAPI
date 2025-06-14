from logging.config import fileConfig

from geoalchemy2 import Geometry, Geography, Raster
from geoalchemy2.admin import _check_spatial_type
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
import os
from dotenv import load_dotenv, find_dotenv
from app.db import Base
from app.core.config import settings
from app.db.models import *

config = context.config
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
load_dotenv(find_dotenv())
database_url = os.getenv("DATABASE_URL")
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def render_item(obj_type, obj, autogen_context):
  if obj_type == 'type' and isinstance(obj, (Geometry, Geography, Raster)):
    import_name = obj.__class__.__name__
    autogen_context.imports.add(f"from geoalchemy2 import {import_name}")
    return "%r" % obj

  return False


def include_object(object, name, type_, reflected, compare_to):
  if type_ == "table" and name in ("us_lex", "us_gaz", "us_rules", "pointcloud_formats"):
    return False

  if type_ == "index":
    if len(object.expressions) == 1:
      try:
        col = object.expressions[0]
        if (
            _check_spatial_type(col.type, (Geometry, Geography, Raster))
            and col.type.spatial_index
        ):
          return False
      except AttributeError:
        pass
  if type_ == "table" and name == "spatial_ref_sys":
    return False

  return True


def run_migrations_offline() -> None:
    url = database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_item=render_item,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
      connection=connection,
      target_metadata=target_metadata,
      render_item=render_item,
      include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
      config.get_section(config.config_ini_section),
      prefix="sqlalchemy.",
      poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())