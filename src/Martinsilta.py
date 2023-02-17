import os
from datetime import datetime

import discord
from dotenv import load_dotenv

from src.libs.safkaonline.SafkaOnline import SafkaMenu
from src.modules.MenuModule import MenuModule

# Load .env file
load_dotenv()

# Create client
client = discord.Bot()


# When the bot is ready
@client.event
async def on_ready():
    print('Bot launching...')

    # Modules dependent on the bot being ready
    client.load_extension("src.modules.ExamPingModule")

client.load_extension("src.modules.MenuModule")

# Launch the bot
client.run(os.getenv('DISCORD_TOKEN'))
