from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from config import DATABASE_NAME, DATABASE_URL

client = AsyncIOMotorClient(DATABASE_URL)
engine = AIOEngine(client=client, database=DATABASE_NAME)

__all__ = ["client", "engine"]
