import logging

import discord
from discord.ext import commands


class MartinsiltaModule(commands.Cog):
    def __init__(self, dcbot: discord.Bot):
        self.dcbot = dcbot
        self.logger = logging.getLogger(f"Martinsilta.{self.__class__.__name__}")
        self.version = "2.0"
