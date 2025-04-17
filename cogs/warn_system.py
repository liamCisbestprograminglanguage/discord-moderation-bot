import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta

class warn_system(commands.Cog):
    def __init__(self, bot, warns_file="storage/warns.json", history_file="storage/warns_history.json", moderators_file="storage/moderator.json", user_timeout=60, warn_timeout=86400):
        self.bot = bot
        self.warns_file = warns_file
        self.history_file = history_file
        self.moderators_file = moderators_file
        self.user_timeout = user_timeout
        self.warn_timeout = warn_timeout

    def load_data(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

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
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        if not await self.is_moderator(ctx):
            return

        warns = self.load_data(self.warns_file)
        history = self.load_data(self.history_file)

        user_id = str(member.id)
        if user_id not in warns:
            warns[user_id] = []

        warns[user_id].append({
            "reason": reason,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        await ctx.send(f"{member.mention} has been warned for: {reason}")

        if len(warns[user_id]) >= 3:
            try:
                await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=self.warn_timeout))
                await ctx.send(f"{member.mention} has been timed out for 1 day due to accumulating 3 warnings.")
            except discord.Forbidden:
                await ctx.send(f"Failed to timeout {member.mention}")

            if user_id not in history:
                history[user_id] = []
            history[user_id].extend(warns[user_id])
            warns[user_id] = []

        self.save_data(self.warns_file, warns)
        self.save_data(self.history_file, history)

    @commands.command()
    async def checkwarns(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return

        warns = self.load_data(self.warns_file)
        user_id = str(member.id)

        if user_id in warns and warns[user_id]:
            warn_list = "\n".join(
                [f"{i+1}. {warn['reason']} (Date: {warn['date']})" for i, warn in enumerate(warns[user_id])]
            )
            await ctx.send(f"{member.mention} has the following warnings:\n{warn_list}")
        else:
            await ctx.send(f"{member.mention} has no active warnings.")

    @commands.command()
    async def checkwarnshistory(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return

        history = self.load_data(self.history_file)
        user_id = str(member.id)

        if user_id in history and history[user_id]:
            warn_list = "\n".join(
                [f"{i+1}. {warn['reason']} (Date: {warn['date']})" for i, warn in enumerate(history[user_id])]
            )
            await ctx.send(f"{member.mention} has the following warning history:\n{warn_list}")
        else:
            await ctx.send(f"{member.mention} has no warning history.")

    @commands.command()
    async def clearwarns(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return

        warns = self.load_data(self.warns_file)
        user_id = str(member.id)

        if user_id in warns:
            warns.pop(user_id)
            self.save_data(self.warns_file, warns)
            await ctx.send(f"Cleared all active warnings for {member.mention}.")
        else:
            await ctx.send(f"{member.mention} has no active warnings to clear.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("warn_system is online!")

async def setup(bot):
    await bot.add_cog(warn_system(bot))