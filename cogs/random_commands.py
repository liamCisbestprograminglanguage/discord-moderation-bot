import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta
import random

class random_commands(commands.Cog):
    def __init__(self, bot, funfacts_file="storage/funfacts.json", moderators_file="storage/moderator.json", user_timeout=60):
        self.bot = bot
        self.funfacts_file = funfacts_file
        self.moderators_file = moderators_file
        self.user_timeout = user_timeout

    def load_data(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_data(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    async def is_moderator(self, ctx):
        moderators = self.load_data(self.moderators_file)
        if str(ctx.author.id) not in moderators:
            try:
                await ctx.author.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=self.user_timeout))
                await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command. You have been timed out for 1 minute.")
            except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return False
        return True

    @commands.command()
    async def funfact(self, ctx):
        funfacts = self.load_data(self.funfacts_file)
        if funfacts:
            random_fact = random.choice(funfacts)
            await ctx.send(f"Fun Fact: \n {random_fact}")
        else:
            await ctx.send("No fun facts available. Add some using `.addfunfact`!")

    @commands.command()
    async def addfunfact(self, ctx, *, fact: str):
        if not await self.is_moderator(ctx):
            return

        funfacts = self.load_data(self.funfacts_file)
        funfacts.append(fact)
        self.save_data(self.funfacts_file, funfacts)
        await ctx.send(f"fun fact added: \"{fact}\"")

    @commands.Cog.listener()
    async def on_ready(self):
        print("random_commands is online!")

async def setup(bot):
    await bot.add_cog(random_commands(bot))