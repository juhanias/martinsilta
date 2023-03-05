import os

import discord
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Create client
client = discord.Bot(intents=discord.Intents.all())


# When the bot is ready
@client.event
async def on_ready():
    print('Bot launching...')

    # Modules dependent on the bot being ready
    # client.load_extension("src.modules.ExamPingModule")
    # client.load_extension("src.modules.FoliAnnouncementPingModule")


client.load_extension("src.modules.BussitutkaModule")
# client.load_extension("src.modules.MenuModule")

# Launch the bot
client.run(os.getenv('DISCORD_TOKEN'))
