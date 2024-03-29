from gino import Gino

db = Gino()

from botler import utils
import botler.database.models as models


async def setup():
    await db.set_bind(utils.config.database_uri)


async def shutdown():
    await db.pop_bind().close()


async def query_guild(guild_id: int):
    """query guild, create if not exist"""
    guild = await models.Guild.get(guild_id)
    if guild is None:
        guild = await models.Guild.create(id=guild_id)
    return guild


async def delete_guild(guild_id: int):
    """delete guild by id"""
    await models.Guild.delete.where(models.Guild.id == guild_id).gino.status()
