import os

import discord
from discord.ext import tasks

from src.MartinsiltaModule import MartinsiltaModule
from src.libs.wilmapy.Wilma import Wilma
from src.libs.wilmapy.WilmaUtils import isExamInDatabase, pushExamToDatabase


class ExamPingModule(MartinsiltaModule):
    def __init__(self, bot: discord.Bot):
        super().__init__(bot)
        self.logger.info("Exam ping module initialized")

    @tasks.loop(
        minutes=30
    )
    async def fetch_exam_data(self):
        self.logger.info("Fetching exam data")
        # Fetch exam data - AMIS TIEV22N
        wilma_instance = Wilma(os.getenv("WILMA_AMIS_TIEV22N_MAIL"),
                               os.getenv("WILMA_AMIS_TIEV22N_PASS"),
                               os.getenv("WILMA_AMIS_TIEV22N_ID"))
        wilma_instance.initialize_connection()
        for exam in wilma_instance.get_past_exams():
            if exam.has_been_graded():
                if not isExamInDatabase(exam):
                    self.logger.info("New exam found")
                    pushExamToDatabase(exam)
                    emb = discord.Embed(
                        title="☝️ Martinsillan Botti huomasi uusia koetuloksia Wilmassa.",
                        url="https://turku.inschool.fi/",
                        description=f"**Kokeen nimi:** {exam.name}\n**Kurssi:** {exam.course_fullname}",
                        color=discord.Color.random())
                    emb.set_author(name=exam.name, url="https://turku.inschool.fi/")
                    emb.set_footer(text=f"{exam.date_humanreadable} - {exam.name} - {exam.course_fullname}")
                    await self.dcbot.get_channel(int(os.getenv("DISCORD_AMISEXAMS_TIEV22N_CHANNEL"))).send(
                        content=f"<@&{os.getenv('DISCORD_PING_AMISEXAMS_TIEV22N')}> koetuloksia tuli wilmaan :flushed: vitosia tietenkin kaikilla??",
                        embed=emb
                    )
        self.logger.info(wilma_instance.logout())

def setup(bot):
    bot.add_cog(ExamPingModule(bot))
    bot.get_cog("ExamPingModule").fetch_exam_data.start()