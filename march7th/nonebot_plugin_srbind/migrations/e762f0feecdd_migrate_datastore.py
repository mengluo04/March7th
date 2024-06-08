"""migrate datastore

迁移 ID: e762f0feecdd
父迁移: 8ab00aaa7483
创建时间: 2024-06-08 17:23:45.312346

迁移代码参考: https://github.com/he0119/nonebot-plugin-wordcloud
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from alembic.op import run_async
from sqlalchemy.orm import Session
from nonebot import logger, require
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Connection, select, inspect
from sqlalchemy.ext.asyncio import AsyncConnection

revision: str = "e762f0feecdd"
down_revision: str | Sequence[str] | None = "8ab00aaa7483"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _migrate_old_data(ds_conn: Connection):
    insp = inspect(ds_conn)
    if (
        "nonebot_plugin_srbind_userbind" not in insp.get_table_names()
        or "nonebot_plugin_srbind_alembic_version" not in insp.get_table_names()
    ):
        logger.debug("No datastore database of plugin nonebot_plugin_srbind")
        return

    DsBase = automap_base()
    DsBase.prepare(autoload_with=ds_conn)
    DsUserBind = DsBase.classes.nonebot_plugin_srbind_userbind

    Base = automap_base()
    Base.prepare(autoload_with=op.get_bind())
    UserBind = Base.classes.nonebot_plugin_srbind_userbind

    ds_session = Session(ds_conn)
    session = Session(op.get_bind())

    count = ds_session.query(DsUserBind).count()
    if count == 0:
        logger.info("No datastore data of plugin nonebot_plugin_srbind")
        return

    AlembicVersion = DsBase.classes.nonebot_plugin_srbind_alembic_version
    version_num = ds_session.scalars(select(AlembicVersion.version_num)).one_or_none()
    if not version_num:
        return
    if version_num != "ad4d0321eed8":
        logger.warning(
            "Old database is not latest version, "
            "please use `nb datastore upgrade` in v0.2.0 first"
        )
        raise RuntimeError(
            "You should upgrade old database in v0.2.0 first to migrate data"
        )

    logger.info("Migrating nonebot_plugin_srbind data from datastore")
    user_bind_list = ds_session.query(DsUserBind).all()
    for user_bind in user_bind_list:
        session.add(
            UserBind(
                id=user_bind.id,
                bot_id=user_bind.bot_id,
                user_id=user_bind.user_id,
                sr_uid=user_bind.sr_uid,
                mys_id=user_bind.mys_id,
                device_id=user_bind.device_id,
                device_fp=user_bind.device_fp,
                cookie=user_bind.cookie,
                stoken=user_bind.stoken,
            )
        )
    session.commit()
    logger.success("Migrate nonebot_plugin_srbind data from datastore successfully")


async def data_migrate(conn: AsyncConnection):
    from nonebot_plugin_datastore.db import get_engine

    async with get_engine().connect() as ds_conn:
        await ds_conn.run_sync(_migrate_old_data)


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        require("nonebot_plugin_datastore")
    except RuntimeError:
        return

    run_async(data_migrate)
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
