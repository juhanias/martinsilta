import json
import os
from datetime import datetime

import discord
import requests
from discord import Color


class SafkaMenu:
    def __init__(self, from_cache=True):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"Martinsilta/1.0.0 (python-requests/{requests.__version__})",
            "Accept": "application/json",
            "From": "juhani.astikainen@gmail.com w/ love"})

        # Force cache refresh on Monday
        if from_cache and datetime.today().weekday() != 0:
            if not os.path.exists("libs/safkaonline/cache"):
                os.mkdir("libs/safkaonline/cache")

            if not os.path.exists("src/libs/safkaonline/cache/menu.json"):
                with open("libs/safkaonline/cache/menu.json", "a+", encoding="utf-8") as f:
                    self.json_menu = self.session.get("https://api.safka.online/v1/menu").json()
                    self.days = [SafkaDay(date_json) for date_json in self.json_menu["days"]]
                    f.write(json.dumps(self.json_menu))
                    f.close()
            else:
                with open("libs/safkaonline/cache/menu.json", "r", encoding="utf-8") as f:
                    self.json_menu = json.load(f)
                    self.days = [SafkaDay(date_json) for date_json in self.json_menu["days"]]

        else:
            self.json_menu = self.session.get("https://api.safka.online/v1/menu").json()
            self.days = [SafkaDay(date_json) for date_json in self.json_menu["days"]]

    def formWeekEmbed(self, version):
        ruokastr = ""
        for day in self.days[0:5]:
            daystr = datetime.strptime(day.date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")
            ruokastr += f"**{self.dayIntToStr(day.dayId)} - {daystr}**\n"
            for dish in day.dishes:
                ruokastr += f"`{dish.name}`\n"
            ruokastr += "\n"

        embed = discord.Embed(
            title=f"Juhannuskukkulan viikon ruokalista - {datetime.today().strftime('%d.%m.%Y')}",
            description=f"{ruokastr}",
            color=Color.random()
        )
        embed.set_author(
            name=f"Martinsilta v{version}",
        )
        embed.set_footer(
            text="Martinsilta",
        )

        return embed

    def formDayEmbed(self, day, version):
        daystr = datetime.strptime(self.days[day].date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")
        ruokastr = f"**{self.dayIntToStr(self.days[day].dayId)} - {daystr}**\n"
        for dish in self.days[day].dishes:
            ruokastr += f"`{dish.name}`\n"
        ruokastr += "\n"

        embed = discord.Embed(
            title=f"Juhannuskukkulan {self.dayIntToStr(self.days[day].dayId)}n ruokalista - {datetime.today().strftime('%d.%m.%Y')}",
            description=f"{ruokastr}",
            color=Color.random()
        )
        embed.set_author(
            name=f"Martinsilta v{version}",
        )
        embed.set_footer(
            text="Martinsilta",
        )

        return embed
    @staticmethod
    def dayIntToStr(dayint: int):
        if dayint == 0:
            return "Maanantai"
        elif dayint == 1:
            return "Tiistai"
        elif dayint == 2:
            return "Keskiviikko"
        elif dayint == 3:
            return "Torstai"
        elif dayint == 4:
            return "Perjantai"
        elif dayint == 5:
            return "Lauantai"
        elif dayint == 6:
            return "Sunnuntai"


class SafkaDay:
    def __init__(self, date_json):
        self._hash = date_json["hash"]
        self.dayId = date_json["dayId"]
        self.date = date_json["date"]
        self.dishes = [SafkaDish(dish_json) for dish_json in date_json["menu"]]


class SafkaDish:
    def __init__(self, dish_json):
        self.name = dish_json["name"]
        self.isLactoseFree = dish_json["isLactoseFree"]
        self.isGlutenFree = dish_json["isGlutenFree"]
        self.isDairyFree = dish_json["isDairyFree"]
