import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta

class helpCog(commands.Cog):
    def __init__(self, bot, moderators_file="storage/moderator.json", user_timeout=60):
        self.bot = bot
        self.moderators_file = moderators_file
        self.user_timeout = user_timeout

    def load_data(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

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
    async def help(self, ctx, ):
        if not await self.is_moderator(ctx):
            return

        help_message = """All commands:

        **WARN SYSTEM:**
        `.warn @user reason` - Once a user reaches 3 warns, they will be timed out for a day.
        `.checkwarns @user` - Sends a list of active warns for that specific user.
        `.checkwarnshistory @user` - Sends a list of previous warns.
        `.clearwarns @user` - Clears the user's active warns.
    
        **OPERATOR COMMANDS:**
        `.moderator @user` - Gives the user moderator permissions.
        `.demoderator @user` - Removes the user's moderator permissions.
        `.giverole @user roleID` - Assigns a role to the user.
        `.removerole @user roleID` - Removes a role from the user.
        `.listroles` - Lists all roles you can assign to someone.
        """

        await ctx.send(help_message)

    @commands.command()
    async def listroles(self, ctx, ):
        if not await self.is_moderator(ctx):
            return

        roles = """
        **ROLES:**
        `1328810843022037123` - Recognized mf
        `1328810659344814120` - Acknowledged mf
        `1326907067562201214` - Regular mf
        `1330268862851055626` - gay fuck idiot
        `1332812354089517127` - image perms
        """

        await ctx.send(roles)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("help is online!")

async def setup(bot):
    await bot.add_cog(helpCog(bot))