import os

import discord
from discord.ext import commands, tasks

from src.MartinsiltaModule import MartinsiltaModule
from src.libs.folipy.Foli import Foli
from src.libs.folipy.FoliUtils import isAnnouncementInDatabase, pushMessageToDatabase


class FoliAnnouncementPingModule(MartinsiltaModule):
    def __init__(self, bot: discord.Bot):
        super().__init__(bot)
        self.logger.info("Foli announcement ping module initialized")
        self.folisession = Foli()

    # new scheduler that runs every 5 minutes
    # if the announcement is different from the previous one, ping the role

    @tasks.loop(
        minutes=5
    )
    async def fetch_announcement_data(self):
        for announcement in self.folisession.get_announcements()[2]:
            if not isAnnouncementInDatabase(announcement):
                self.logger.info("New announcement found")
                emb = discord.Embed(
                    title=f"FÖLI: {announcement['header']}",
                    url="https://www.foli.fi/",
                    description=f"{announcement['message']}",
                    color=discord.Color.random())

                try:
                    emb.add_field(name="Kategoria", value=f"{self.folisession.cache[announcement['categories'][0]]}", inline=False)
                except IndexError:
                    emb.add_field(name="Kategoria", value="Ei kategoriaa", inline=False)

                try:
                    emb.set_image(url=f'http:{announcement["images"][0]["url"]}')
                except IndexError:
                    pass
                except KeyError:
                    pass

                await self.dcbot.get_channel(int(os.getenv("DISCORD_FOLIALERTS_CHANNEL"))).send(
                    content=f"Uusi tiedote Föliltä! <@&{os.getenv('DISCORD_PING_FOLIALERTS')}>",
                    embed=emb
                )

                # push announcement to database
                pushMessageToDatabase(announcement)

def setup(bot):
    bot.add_cog(FoliAnnouncementPingModule(bot))
    bot.get_cog("FoliAnnouncementPingModule").fetch_announcement_data.start()