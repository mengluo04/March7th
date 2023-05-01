from typing import List, Optional

from nonebot_plugin_datastore import create_session, get_plugin_data
from sqlalchemy import TEXT, String, select, update
from sqlalchemy.orm import Mapped, mapped_column

plugin_data = get_plugin_data()
Model = plugin_data.Model


class UserBind(Model):
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[str] = mapped_column(String(64))
    sr_uid: Mapped[str] = mapped_column(String(64))
    mys_id: Mapped[Optional[str]] = mapped_column(String(64))
    cookie: Mapped[Optional[str]] = mapped_column(TEXT)
    stoken: Mapped[Optional[str]] = mapped_column(TEXT)


async def set_user_srbind(user: UserBind) -> None:
    select_user = await get_user_srbind(user.bot_id, user.user_id)
    select_uid = [user.sr_uid for user in select_user]
    if user.sr_uid in select_uid:
        old_user = select_user[select_uid.index(user.sr_uid)]
        statement = (
            update(UserBind)
            .where(UserBind.id == old_user.id)
            .values(cookie=user.cookie, stoken=user.stoken)
        )
        async with create_session() as session:
            await session.scalars(statement)
            await session.commit()
    else:
        async with create_session() as session:
            session.add(user)
            await session.commit()


async def del_user_srbind(bot_id: str, user_id: str, sr_uid: str) -> None:
    select_user = await get_user_srbind(bot_id, user_id)
    select_uid = [user.sr_uid for user in select_user]
    if sr_uid in select_uid:
        user = select_user[select_uid.index(sr_uid)]
        async with create_session() as session:
            await session.delete(user)
            await session.commit()


async def get_user_srbind(bot_id: str, user_id: str) -> List[UserBind]:
    statement = (
        select(UserBind)
        .where(UserBind.bot_id == bot_id)
        .where(UserBind.user_id == user_id)
    )
    async with create_session() as session:
        records = (await session.scalars(statement)).all()
    return list(records)
