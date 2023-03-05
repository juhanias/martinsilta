import discord
import requests
from discord import SlashCommandOptionType, option
from discord.ext import tasks, commands

from src.MartinsiltaModule import MartinsiltaModule
from src.libs.folipy import Foli, cache
from src.libs.folipy.Foli import Stop


class BussitutkaModule(MartinsiltaModule):
    def __init__(self, bot: discord.Bot):
        super().__init__(bot)
        self.bussitutka = Foli.Bussitutka()
        cache.latest_gtfs_dataset = requests.get("http://data.foli.fi/gtfs/v0/").json()["latest"]
        stops_data = requests.get("http://data.foli.fi/gtfs/v0/" + cache.latest_gtfs_dataset + "/stops").json()
        cache.stops_cache = {}
        cache.tasks_cache = {}
        for stop in stops_data:
            cache.stops_cache[stops_data[stop]['stop_code']] = Stop(stops_data[stop])

        cache.vehicles_cache = self.bussitutka.get_live_vehicles()

        self.update_tasks.start()

    # make a slash command for this
    @commands.slash_command(
        name="bussitutka",
        description="Missä bussi? Bussitutka antaa sinulle päivittyvää tietoa bussisi sijainnista.",
    )
    @option(
        name="linja",
        description="Linjan numero (esim. 18)",
        required=True,
        input_type=SlashCommandOptionType.string
    )
    @option(
        name="pysakki",
        description="Pysäkin numero (esim. 1234)",
        required=True,
        input_type=SlashCommandOptionType.string
    )
    async def bussitutka(self,
                         ctx: discord.ApplicationContext,
                         linja: str,
                         pysakki: str):
        # check if the stop exists
        if pysakki not in cache.stops_cache:
            print(cache.stops_cache)
            await ctx.respond(f"**Virhekoodi 1**\n`Pysäkkiä {pysakki} ei löytynyt.`")
            return

        # check if the vehicle exists
        existing_vehicles = [vehicle.line_ref for vehicle in cache.vehicles_cache]
        if linja not in existing_vehicles:
            await ctx.respond(f"**Virhekoodi 2**\n`Linjaa {linja} ei löytynyt liikenteestä.`")
            return

        # check if the vehicle is relevant to the stop
        closest_vehicles = cache.stops_cache[pysakki].get_closest_vehicle(linja)
        closest_vehicle = closest_vehicles[0] if len(closest_vehicles) > 0 else None
        if closest_vehicle is None:
            await ctx.respond(
                f"**Virhekoodi 3**\n`Linja {linja} ei näytä kulkevan pysäkin {pysakki} kautta, ainakaan lähiaikoihin.`")
            return

        # check if the user already has a task running
        if ctx.author.id in cache.tasks_cache:
            await ctx.respond(
                f"**Virhekoodi 4**\n`Valvot jo pysäkkiä {cache.tasks_cache[ctx.user.id].taskStop}. Et voi aloittaa toista tutkaa.`")
            return
        else:
            print(cache.tasks_cache)

        response_embed_1 = discord.Embed(
            title=f"Bussitutka valvoo linjaa {linja} pysäkiltä {pysakki}"
        )

        response_embed_1.description = ""

        response_embed_1.description += f"**Lähin ajoneuvo**\n🚌 **{closest_vehicle.line_ref} - {closest_vehicle.vehicle_data['destinationdisplay']}** (<t:{closest_vehicle.vehicle_data['expecteddeparturetime']}:R>)\n\n**Muut ajoneuvot**\n"

        for vehicle in closest_vehicles[1]:
            print(vehicle)
            response_embed_1.description += f"🚌 **{vehicle.line_ref} - {vehicle.vehicle_data['destinationdisplay']}** (<t:{vehicle.vehicle_data['expecteddeparturetime']}:R>)\n"

        response_embed_2 = discord.Embed(
            title=f"Lähin bussi"
        )

        closest_vehicle_cache = None
        for vehicle in cache.vehicles_cache:
            print(vehicle)
            if vehicle.vehicle_ref == closest_vehicle.vehicle_ref:
                print("found")
                closest_vehicle_cache = vehicle
                break

        print(closest_vehicle_cache.vehicle_data)
        response_embed_2.description = f"🚌 {closest_vehicle.line_ref} - {closest_vehicle.vehicle_data['destinationdisplay']}\n\n**Seuraava pysäkki: {closest_vehicle_cache.vehicle_data['next_stoppointname']}\n**Aikataulun mukainen saapumisaika: <t:{closest_vehicle.vehicle_data['aimeddeparturetime']}:R>**\n**Odotettu saapumisaika: <t:{closest_vehicle.vehicle_data['expecteddeparturetime']}:R>\n\n"

        response_embed_2.description += f"**Saapuu pysäkillesi (arvio): <t:{closest_vehicle.vehicle_data['expectedarrivaltime']}:t>**\n\n"
        message = await ctx.respond(embeds=[response_embed_1, response_embed_2], view=self.BussitutkaView())
        # if everything is ok, start the task
        cache.tasks_cache[ctx.author.id] = Foli.BussitutkaTask(
            {
                "taskAuthor": ctx.user,
                "taskChannel": ctx.channel,
                "taskMessage": message,
                "taskStop": pysakki,
                "taskLine": linja,
            }
        )

    @tasks.loop(
        seconds=10
    )
    async def update_tasks(self):
        if len(cache.tasks_cache) == 0:
            return

        cache.vehicles_cache = self.bussitutka.get_live_vehicles()

        for task in cache.tasks_cache:
            await cache.tasks_cache[task].update(self.dcbot)

    class BussitutkaView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = None

        @discord.ui.button(label="Lopeta valvominen", style=discord.ButtonStyle.danger, emoji="🛑", )
        async def stop_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.message.delete()
            await interaction.channel.send(
                f"**Valvonta pysäkiltä {cache.tasks_cache[interaction.user.id].taskStop} lopetettu.**")
            del cache.tasks_cache[interaction.user.id]


def setup(bot):
    bot.add_cog(BussitutkaModule(bot))
