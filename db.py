# TODO: add database engine and entrypoint
# TODO: hide db username and password in .env file
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings import settings

engine = create_async_engine(settings.db.url)
AsyncSessionMaker = async_sessionmaker(
    engine,
    class_= AsyncSession,
    expire_on_commit=False
    
)

async def get_db():
   async with AsyncSessionMaker() as session:
        yield session