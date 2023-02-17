import os
from datetime import time, timezone, datetime

import discord
from discord.ext import tasks

from src.MartinsiltaModule import MartinsiltaModule
from src.libs.safkaonline.SafkaOnline import SafkaMenu


class MenuModule(MartinsiltaModule):
    def __init__(self, bot: discord.Bot):
        super().__init__(bot)
        self.logger.info("Menu module initialized")

    @tasks.loop(
        time=time(4, 0, tzinfo=timezone.utc)
    )  # Task that runs every day at 6 AM Helsinki time
    async def broadcast_menu(self):
        self.logger.info("Broadcasting menu")
        if datetime.today().weekday() in (5, 6):
            return

        # Broadcast the menu
        channel = self.dcbot.get_channel(int(os.getenv("DISCORD_MENU_CHANNEL")))

        if datetime.today().weekday() == 0:
            await channel.send(embed=SafkaMenu(from_cache=True).formWeekEmbed(self.version),
                               content=f"<@&{os.getenv('DISCORD_PING_MENU')}> Viikon ruokalista on täällä!")
        else:
            await channel.send(embed=SafkaMenu(from_cache=True).formDayEmbed(datetime.today().weekday(), self.version),
                               content=f"<@&{os.getenv('DISCORD_PING_MENU')}> huomenta :wave: tässä päivän ruoka:")


def setup(bot):
    bot.add_cog(MenuModule(bot))
    bot.get_cog("MenuModule").broadcast_menu.start()
