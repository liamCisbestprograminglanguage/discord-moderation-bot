import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta
from typing import Optional

class operators(commands.Cog):
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
    async def moderator(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return

        moderators = self.load_data(self.moderators_file)

        user_id = str(member.id)
        if user_id not in moderators:
            moderators[user_id] = True
            self.save_data(self.moderators_file, moderators)
            await ctx.send(f"{member.mention} has been granted moderator permissions.")
        else:
            await ctx.send(f"{member.mention} is already a moderator.")

    @commands.command()
    async def demoderator(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return

        moderators = self.load_data(self.moderators_file)

        user_id = str(member.id)
        if user_id in moderators:
            moderators.pop(user_id)
            self.save_data(self.moderators_file, moderators)
            await ctx.send(f"{member.mention} has been removed from moderator permissions.")
        else:
            await ctx.send(f"{member.mention} is not a moderator.")

    @commands.command()
    async def giverole(self, ctx, member: discord.Member, role_id: int):
        if not await self.is_moderator(ctx):
            return

        role = ctx.guild.get_role(role_id)

        if not role:
            await ctx.send("The specified role does not exist. Please check the role ID.")
            return

        allowed_roles = [1328810843022037123, 1328810659344814120, 1326907067562201214, 1330268862851055626, 1332812354089517127]

        if role_id not in allowed_roles:
            await ctx.send("Permission Denied.")
            return

        try:
            await member.add_roles(role)
            await ctx.send(f"{member.mention} has been given the role '{role.name}'.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to assign this role.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while assigning the role: {e}")

    @commands.command()
    async def removerole(self, ctx, member: discord.Member, role_id: int):
        if not await self.is_moderator(ctx):
            return
        
        role = ctx.guild.get_role(role_id)

        if not role:
            await ctx.send("The specified role does not exist. Please check the role ID.")
            return

        allowed_roles = [1328810843022037123, 1328810659344814120, 1326907067562201214, 1330268862851055626, 1332812354089517127]

        if role_id not in allowed_roles:
            await ctx.send("Permission Denied.")
            return

        try:
            await member.remove_roles(role)
            await ctx.send(f"The role '{role.name}' has been removed from {member.mention}.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to remove this role.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while removing the role: {e}")

    @commands.command()
    async def timeout(self, ctx, member: discord.Member, length: int):
        if not await self.is_moderator(ctx):
            return

        try:
            timeout_duration = discord.utils.utcnow() + timedelta(hours=length)
            await member.edit(timed_out_until=timeout_duration)
            if length == 1:
                await ctx.send(f"{member.mention} has been timed out for {length} hour.")
            else:
                await ctx.send(f"{member.mention} has been timed out for {length} hours.")
        except ValueError:
            await ctx.send("Please provie a valid number for timeout duration.")
            return
        except discord.Forbidden:
            await ctx.send(f"Failed to timeout user {member.mention}")

    @commands.command()
    async def removetimeout(self, ctx, member: discord.Member):
        if not await self.is_moderator(ctx):
            return
        
        try:
            timeout = discord.utils.utcnow() + timedelta(seconds=1)
            await member.edit(timed_out_until=timeout)
        except discord.Forbidden:
            await ctx.send("Failed to remove timeout")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if not await self.is_moderator(ctx):
            return
        
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been Kicked from the server.")
        except discord.Forbidden:
            await ctx.send(f"Failed to kick member {member.mention}")
    
    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if not await self.is_moderator(ctx):
            return
        
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been Banned from the server.")
        except discord.Forbidden:
            await ctx.send(f"Failed to ban member {member.mention}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("operators is online!")

async def setup(bot):
    await bot.add_cog(operators(bot))