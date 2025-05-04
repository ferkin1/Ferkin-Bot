import sqlalchemy as sqla
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE")
engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class SteamProfileDB(Base):
    __tablename__="steam_profiles"

    discord_id = sqla.Column(sqla.String, primary_key=True)
    steam_id = sqla.Column(sqla.String, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def link_steam_profile(_discord_id:str, _steam_id:str):
    async with SessionLocal() as session:
        profile = await session.get(SteamProfileDB, _discord_id)
        if profile:
            profile.steam_id = _steam_id
        else:
            session.add(SteamProfileDB(discord_id=_discord_id, steam_id=_steam_id))
        await session.commit()

async def get_profile(_discord_id:str):
    async with SessionLocal() as session:
        profile = await session.get(SteamProfileDB, _discord_id)
        return profile.steam_id if profile else None

async def unlink_profile(_discord_id:str):
    async with SessionLocal() as session:
        profile = await session.get(SteamProfileDB, _discord_id)
        if profile:
            await session.delete(profile)
            await session.commit()

async def list_profiles():
    async with SessionLocal() as session:
        result = await session.execute(sqla.select(SteamProfileDB))
        return result.scalars().all()