from discord.ext import commands
from context import HungryContext


class HungryBot(commands.Bot):
    async def on_message(self, message):
        ctx = await self.get_context(message, cls=HungryContext)
        await self.invoke(ctx)
